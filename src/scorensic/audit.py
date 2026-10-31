"""Load an eval spec, run probes against its grader, and turn results into findings."""
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import __version__, probes as probe_lib

WORKER = Path(__file__).with_name("_worker.py")
SEVERITY = {
    "accepts_wrong_answer": "high",
    "rejects_reference": "high",
    "answer_leak": "high",
    "grader_visible": "high",
    "nondeterministic_score": "medium",
    "rejects_valid_answer": "medium",
    "grader_error": "low",
}
REMEDIATION = {
    "accepts_wrong_answer": "Compare a normalised, parsed answer for equality instead of substring/regex presence; add this output as a known_wrong regression case.",
    "rejects_reference": "The task's own reference fails its grader: fix the grader or the reference before scoring anyone.",
    "rejects_valid_answer": "Normalise formatting (whitespace, case, numeric form) before comparing, or list accepted alternatives explicitly.",
    "nondeterministic_score": "Remove randomness, time and shared mutable state from the grader, or fix the seed and record it.",
    "answer_leak": "Move expected answers and grading files out of anything the agent can read (workspace, prompt, image, git history).",
    "grader_visible": "Keep grader code and expected outputs outside the agent-visible paths and mount them only at grading time.",
    "grader_error": "Make the grader return a fail score on malformed output instead of raising; decide explicitly how the harness treats grader errors.",
}
LEAK_MIN_CHARS = 4  # shortcut: shorter references match everywhere; skip and report as skipped.
PROMPT_LEAK_MIN_CHARS = 12


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_spec(eval_dir):
    eval_dir = Path(eval_dir).resolve()
    spec_path = eval_dir / "eval.json"
    if not spec_path.is_file():
        raise SystemExit(f"error: {spec_path} not found (an eval directory needs eval.json)")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for key in ("grader", "tasks"):
        if key not in spec:
            raise SystemExit(f"error: eval.json is missing '{key}'")
    tasks_path = (eval_dir / spec["tasks"]).resolve()
    tasks = [json.loads(line) for line in tasks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for t in tasks:
        if "id" not in t or "reference" not in t:
            raise SystemExit(f"error: every task needs 'id' and 'reference' ({tasks_path})")
    return eval_dir, spec_path, spec, tasks_path, tasks


def _run_python(eval_dir, grader, calls, repeats, timeout, memory_mb):
    python = grader.get("python", sys.executable)
    cmd = [python, "-I", str(WORKER), str(eval_dir / grader["path"]), grader.get("function", "grade")]
    payload = json.dumps({"calls": calls, "repeats": repeats, "memory_mb": memory_mb})
    try:
        proc = subprocess.run(cmd, input=payload, capture_output=True, text=True, cwd=eval_dir, timeout=timeout)
    except subprocess.TimeoutExpired:
        return [[{"error": f"grader batch exceeded {timeout}s timeout"}] * repeats for _ in calls]
    if proc.returncode != 0:
        err = (proc.stderr.strip().splitlines() or ["no stderr"])[-1][:300]
        return [[{"error": f"grader process failed: {err}"}] * repeats for _ in calls]
    return json.loads(proc.stdout)["results"]


def _run_command(eval_dir, grader, calls, repeats, timeout):
    """Command graders get {"task","output"} on stdin. Exit 0 = pass, or print {"score": x}."""
    results = []
    for call in calls:
        runs = []
        for _ in range(repeats):
            try:
                proc = subprocess.run(grader["command"], input=json.dumps(call), capture_output=True,
                                      text=True, cwd=eval_dir, timeout=timeout)
            except subprocess.TimeoutExpired:
                runs.append({"error": f"timed out after {timeout}s"})
                continue
            try:
                runs.append(float(json.loads(proc.stdout)["score"]))
            except (ValueError, KeyError, TypeError):
                runs.append(1.0 if proc.returncode == 0 else 0.0)
        results.append(runs)
    return results


def _visible_files(eval_dir, visible):
    for rel in visible:
        root = (eval_dir / rel).resolve()
        paths = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file()) if root.exists() else []
        for p in paths:
            if p.stat().st_size <= 1_000_000:
                yield p


def _leak_findings(eval_dir, spec, tasks, tasks_path, grader_files):
    findings, skipped = [], []
    visible = list(_visible_files(eval_dir, spec.get("agent_visible", [])))
    visible_set = {p.resolve() for p in visible}
    for f in [tasks_path, *grader_files]:
        if f.resolve() in visible_set:
            findings.append(_finding("grader_visible", None, "high", "Grading file is inside an agent-visible path",
                                     f"{f.relative_to(eval_dir)} is readable by the agent, so it can read the expected answers or grading logic.",
                                     {"file": str(f.relative_to(eval_dir))}))
    contents = {p: p.read_text(encoding="utf-8", errors="ignore") for p in visible if p.resolve() not in {tasks_path.resolve(), *[g.resolve() for g in grader_files]}}
    for task in tasks:
        ref = str(task["reference"]).strip()
        if len(ref) < LEAK_MIN_CHARS:
            skipped.append({"check": "answer_leak", "task_id": task["id"], "reason": f"reference shorter than {LEAK_MIN_CHARS} characters; a text search would be meaningless"})
            continue
        # Short answers (choices like "true"/"B") legitimately appear in prompts; only long ones are suspicious there.
        if len(ref) < PROMPT_LEAK_MIN_CHARS:
            skipped.append({"check": "answer_leak(prompt)", "task_id": task["id"], "reason": f"reference shorter than {PROMPT_LEAK_MIN_CHARS} characters; short answers are often listed as choices in the prompt"})
        elif ref in str(task.get("prompt", "")):
            findings.append(_finding("answer_leak", task["id"], "high", "Expected answer appears in the prompt",
                                     "The reference answer is a substring of the prompt the agent receives.", {"location": "prompt"}))
        for p, text in contents.items():
            if ref in text:
                findings.append(_finding("answer_leak", task["id"], "high" if len(ref) >= 12 else "medium", "Expected answer is readable by the agent",
                                         f"The reference answer appears verbatim in {p.relative_to(eval_dir)}, which is listed in agent_visible.",
                                         {"location": str(p.relative_to(eval_dir))}))
    return findings, skipped


def _finding(check, task_id, confidence, title, explanation, evidence):
    key = f"{check}|{task_id}|{evidence.get('probe_kind') or evidence.get('location') or evidence.get('file') or ''}"
    return {
        "id": hashlib.sha1(key.encode()).hexdigest()[:12],
        "check": check,
        "severity": SEVERITY[check],
        "confidence": confidence,
        "task_id": task_id,
        "title": title,
        "explanation": explanation,
        "evidence": evidence,
        "remediation": REMEDIATION[check],
    }


def audit(eval_dir, task_filter=None, repeats=None, processes=None):
    started = time.perf_counter()
    eval_dir, spec_path, spec, tasks_path, tasks = load_spec(eval_dir)
    if task_filter:
        tasks = [t for t in tasks if t["id"] in task_filter]
    grader = spec["grader"]
    repeats = repeats or spec.get("repeats", 3)
    processes = processes or spec.get("processes", 2)
    timeout = spec.get("timeout_s", 60)
    threshold = spec.get("pass_threshold", 1.0)

    planned = []  # (task, probe)
    for task in tasks:
        for p in probe_lib.build(task, spec.get("equivalent_transforms", ["trailing_newline"])):
            planned.append((task, p))
    calls = [{"task": t, "output": p["output"]} for t, p in planned]

    runs = [[] for _ in calls]
    for _ in range(processes):  # separate processes catch per-process randomness, repeats catch shared state
        if grader.get("type", "python") == "python":
            batch = _run_python(eval_dir, grader, calls, repeats, timeout, spec.get("memory_mb", 1024))
        else:
            batch = _run_command(eval_dir, grader, calls, repeats, timeout)
        for i, r in enumerate(batch):
            runs[i].extend(r)

    findings = []
    flaky, errors = {}, {}
    for (task, p), results in zip(planned, runs):
        distinct = {json.dumps(round(r, 9) if isinstance(r, float) else r, sort_keys=True) for r in results}  # ignore float noise
        if len(distinct) > 1:
            flaky.setdefault(task["id"], []).append({"probe_kind": p["kind"], "output": p["output"], "results": results})
            continue
        r = results[0]
        if isinstance(r, dict):
            errors.setdefault(task["id"], []).append({"probe_kind": p["kind"], "output": p["output"], "error": r["error"]})
            continue
        passed = r >= threshold
        ev = {"probe_kind": p["kind"], "output": p["output"], "expected": p["expect"], "score": r,
              "pass_threshold": threshold, "runs": len(results)}
        if p["expect"] == "fail" and passed:
            findings.append(_finding("accepts_wrong_answer", task["id"], p["confidence"],
                                     f"Grader accepts a wrong answer ({p['kind']})",
                                     f"The output {p['output']!r} is not the reference {task['reference']!r} or a listed alternative, yet it scored {r} on all {len(results)} runs.", ev))
        elif p["expect"] == "pass" and not passed:
            check = "rejects_reference" if p["kind"] == "reference" else "rejects_valid_answer"
            findings.append(_finding(check, task["id"], p["confidence"],
                                     "Grader rejects the task's own reference answer" if check == "rejects_reference" else f"Grader rejects a valid answer ({p['kind']})",
                                     f"The output {p['output']!r} should be accepted but scored {r} (threshold {threshold}) on all {len(results)} runs.", ev))
    for tid, items in flaky.items():
        findings.append(_finding("nondeterministic_score", tid, "high", "Same input, different scores",
                                 f"{len(items)} probe(s) got different results across {processes} process(es) x {repeats} repeat(s).",
                                 {"probes": items}))
    for tid, items in errors.items():
        findings.append(_finding("grader_error", tid, "high", "Grader raised an error",
                                 f"The grader errored on {len(items)} probe(s) instead of returning a score.", {"probes": items}))

    # Only files inside the eval dir count as grader files (not e.g. an absolute interpreter path).
    candidates = [grader["path"]] if "path" in grader else grader.get("command", [])
    grader_files = [p for p in ((eval_dir / a).resolve() for a in candidates) if p.is_file() and p.is_relative_to(eval_dir)]
    leaks, skipped = _leak_findings(eval_dir, spec, tasks, tasks_path, grader_files)
    findings += leaks
    rank = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: (rank[f["severity"]], f["check"], str(f["task_id"])))
    for f in findings:
        f["reproduce"] = f"scorensic audit {eval_dir.name} --task {f['task_id']}" if f["task_id"] else f"scorensic audit {eval_dir.name}"

    by_check, by_sev = {}, {}
    for f in findings:
        by_check[f["check"]] = by_check.get(f["check"], 0) + 1
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
    return {
        "tool": "scorensic",
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "eval": {
            "name": spec.get("name", eval_dir.name),
            "description": spec.get("description", ""),
            "path": str(eval_dir),
            "spec_sha256": sha256(spec_path),
            "tasks_sha256": sha256(tasks_path),
            "grader_sha256": {str(g.relative_to(eval_dir)): sha256(g) for g in grader_files},
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "cpu_count": os.cpu_count()},
        "config": {"repeats": repeats, "processes": processes, "timeout_s": timeout, "pass_threshold": threshold,
                   "equivalent_transforms": spec.get("equivalent_transforms", ["trailing_newline"]),
                   "agent_visible": spec.get("agent_visible", []), "task_filter": task_filter or None},
        "summary": {"tasks": len(tasks), "probes": len(planned), "grader_calls": sum(len(r) for r in runs),
                    "findings": len(findings), "by_check": by_check, "by_severity": by_sev,
                    "runtime_s": round(time.perf_counter() - started, 3)},
        "findings": findings,
        "skipped": skipped,
        "limitations": [
            "Probes are generic. A grader can pass every probe and still be wrong on inputs no probe covers.",
            "Mutant and hedged-answer probes assume a single correct answer; for open-ended tasks treat them as prompts to look, not proof.",
            "Answer-leak search is a verbatim text match over agent_visible files; encoded, paraphrased or git-history leaks are not detected.",
            "Python graders run in a separate process with a timeout. That is not a security sandbox: only audit graders you trust.",
        ],
    }
