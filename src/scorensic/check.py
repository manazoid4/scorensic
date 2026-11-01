"""Business front door: run a sheet of real tasks on one or more models and produce a plain report card.

Sheet (CSV) columns: question, right_answer. Optional: id, context (text the model may use).
Models are reached through any OpenAI-compatible endpoint: Ollama, LM Studio, llama.cpp, or a cloud API.
Before scoring, the built-in marking is checked with the integrity engine, so the score can be trusted.

Written work (letters, emails) uses rules instead of one right answer. Put this in right_answer:
    rules: must=Financial Ombudsman Service; must=six months|6 months; never=[
Every `must` needs one of its `|` alternatives; no `never` may appear (case-insensitive, whole words).
"""
import csv
import ipaddress
import json
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from . import probes

SYSTEM = "Answer with only the answer itself. No explanation. If you do not know, reply exactly: I don't know"
_NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
LETTER_SYSTEM = ("Write the requested text in full, ready to send. Use the real names, references and facts given. "
                 "Do not leave placeholders. If you cannot do it, reply exactly: I don't know")
NO_ANSWER = {"", "i don't know", "i dont know", "unknown", "n/a"}
RULES_PREFIX = "rules:"


def is_rules(task):
    return str(task["reference"]).strip().lower().startswith(RULES_PREFIX)


def parse_rules(reference):
    """'rules: must=a|b; never=c' -> {'must': [['a','b']], 'never': [['c']]}"""
    out = {"must": [], "never": []}
    for part in str(reference).strip()[len(RULES_PREFIX):].split(";"):
        key, _, val = part.partition("=")
        key, alts = key.strip().lower(), [a.strip() for a in val.split("|") if a.strip()]
        if key not in out or not alts:
            raise ValueError(f"bad rule {part.strip()!r}: use must=... or never=...")
        out[key].append(alts)
    if not out["must"]:
        raise ValueError("rules need at least one must=")
    return out


def _flat(s):
    return " ".join(str(s).translate(str.maketrans("\u2018\u2019\u201c\u201d\u2013\u2014", "''\"\"--")).split()).lower()


def _has(text, phrase):
    p = re.escape(_flat(phrase))
    return re.search(rf"(?<!\w){p}(?!\w)" if phrase[:1].isalnum() and phrase[-1:].isalnum() else p, text) is not None


def rule_failures(task, output):
    """Which rules a written answer breaks. Empty list means it passes."""
    r, text = parse_rules(task["reference"]), _flat(output)
    if _norm(output) in NO_ANSWER:
        return ["no answer"]
    fails = [f"missing: {' / '.join(alts)}" for alts in r["must"] if not any(_has(text, a) for a in alts)]
    fails += [f"must not say: {a}" for alts in r["never"] for a in alts if _has(text, a)]
    return fails


def _norm(s):
    return " ".join(str(s).replace("£", "").replace("$", "").replace("€", "").split()).strip(" .").lower()


def _num(s):
    m = _NUM.fullmatch(_norm(s))
    return float(m.group().replace(",", "")) if m else None


def mark(task, output):
    """Built-in marking: the whole answer must equal the right answer (ignoring case, spacing,
    currency signs and a trailing full stop), or be the same number. Hedging and padding fail.
    Rules tasks (right_answer starting 'rules:') pass only if every must is present and no never is."""
    if is_rules(task):
        return not rule_failures(task, output)
    got, want = _norm(output), _norm(task["reference"])
    if got == want:
        return True
    a, b = _num(output), _num(task["reference"])
    return a is not None and b is not None and abs(a - b) < 1e-9


def load_sheet(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("question") or "").strip()]
    if not rows or "right_answer" not in rows[0]:
        raise SystemExit("error: the sheet needs columns 'question' and 'right_answer'")
    return [{"id": r.get("id") or str(i + 1), "prompt": r["question"].strip(), "context": (r.get("context") or "").strip(),
             "reference": r["right_answer"].strip()} for i, r in enumerate(rows)]


def rule_probes(task):
    """Probes for a rules task: one answer meeting every rule must pass; dropping any must, adding any never,
    blank, "I don't know", and echoing the question or the customer's own message back must all fail."""
    r = parse_rules(task["reference"])
    keep = [alts[0] for alts in r["must"]]
    good = "Dear customer,\n" + "\n".join(f"Point: {k}." for k in keep) + "\nYours sincerely"
    out = [{"kind": "meets_every_rule", "output": good, "expect": "pass"}]
    out += [{"kind": "empty", "output": "", "expect": "fail"}, {"kind": "refusal", "output": "I don't know.", "expect": "fail"}]
    for i, k in enumerate(keep):
        out.append({"kind": f"drops_must_{i}", "output": "\n".join(f"Point: {x}." for j, x in enumerate(keep) if j != i),
                    "expect": "fail"})
    for alts in r["never"]:
        for a in alts:
            out.append({"kind": "says_never", "output": f"{good}\n{a}", "expect": "fail"})
    out.append({"kind": "prompt_echo", "output": task["prompt"], "expect": "fail"})
    if task.get("context"):
        out.append({"kind": "context_echo", "output": task["context"], "expect": "fail"})
    return out


def self_check(tasks):
    """Run the integrity probes against the built-in marking. Returns (tricks_caught, tricks_total, problems)."""
    caught = total = 0
    problems = []
    for t in tasks:
        for p in (rule_probes(t) if is_rules(t) else probes.build(t)):
            ok = mark(t, p["output"])
            if p["expect"] == "fail":
                total += 1
                caught += not ok
                if ok:
                    problems.append(f"task {t['id']}: marking accepted {p['output']!r} ({p['kind']})")
            elif not ok:
                problems.append(f"task {t['id']}: marking rejected a correct form {p['output']!r}")
    return caught, total, problems


def is_local(endpoint):
    host = urlparse(endpoint).hostname or ""
    if host in ("localhost",):
        return True
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback
    except ValueError:
        return False


def ask(endpoint, model, task, api_key=None, timeout=300):
    user = f"{task['context']}\n\n{task['prompt']}" if task["context"] else task["prompt"]
    body = json.dumps({"model": model, "temperature": 0, "messages": [
        {"role": "system", "content": LETTER_SYSTEM if is_rules(task) else SYSTEM}, {"role": "user", "content": user}]}).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", body, headers)
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return data["choices"][0]["message"]["content"] or "", time.perf_counter() - start


def run(sheet, endpoint, models, repeats=2, api_key=None):
    tasks = load_sheet(sheet)
    caught, total, problems = self_check(tasks)
    results = []
    for model in models:
        rows = []
        for t in tasks:
            answers, secs, error = [], [], None
            for _ in range(repeats):
                try:
                    a, s = ask(endpoint, model, t, api_key)
                    answers.append(a.strip())
                    secs.append(s)
                except Exception as exc:  # network/model errors are reported per task, not fatal
                    error = f"{type(exc).__name__}: {exc}"[:200]
                    break
            first = answers[0] if answers else ""
            status = ("error" if error else "no_answer" if _norm(first) in NO_ANSWER
                      else "right" if mark(t, first) else "wrong")
            why = rule_failures(t, first) if is_rules(t) and status == "wrong" else []
            rows.append({"id": t["id"], "question": t["prompt"], "right_answer": t["reference"], "answer": first, "why": why,
                         "status": status, "consistent": len(set(answers)) <= 1 and not error,
                         "seconds": round(sum(secs) / len(secs), 2) if secs else None, "error": error})
        n = len(rows)
        count = lambda k: sum(r["status"] == k for r in rows)
        results.append({"model": model, "right": count("right"), "wrong": count("wrong"), "no_answer": count("no_answer"),
                        "errors": count("error"), "total": n, "consistent": sum(r["consistent"] for r in rows),
                        "avg_seconds": round(sum(r["seconds"] or 0 for r in rows) / max(1, sum(r["seconds"] is not None for r in rows)), 2),
                        "rows": rows})
    return {"tool": "scorensic check", "sheet": str(Path(sheet).name), "endpoint_is_local": is_local(endpoint),
            "endpoint_host": urlparse(endpoint).hostname, "repeats": repeats,
            "marking_check": {"tricks_caught": caught, "tricks_total": total, "problems": problems},
            "models": results}
