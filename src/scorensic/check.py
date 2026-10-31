"""Business front door: run a sheet of real tasks on one or more models and produce a plain report card.

Sheet (CSV) columns: question, right_answer. Optional: id, context (text the model may use).
Models are reached through any OpenAI-compatible endpoint: Ollama, LM Studio, llama.cpp, or a cloud API.
Before scoring, the built-in marking is checked with the integrity engine, so the score can be trusted.
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
NO_ANSWER = {"", "i don't know", "i dont know", "unknown", "n/a"}


def _norm(s):
    return " ".join(str(s).replace("£", "").replace("$", "").replace("€", "").split()).strip(" .").lower()


def _num(s):
    m = _NUM.fullmatch(_norm(s))
    return float(m.group().replace(",", "")) if m else None


def mark(task, output):
    """Built-in marking: the whole answer must equal the right answer (ignoring case, spacing,
    currency signs and a trailing full stop), or be the same number. Hedging and padding fail."""
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


def self_check(tasks):
    """Run the integrity probes against the built-in marking. Returns (tricks_caught, tricks_total, problems)."""
    caught = total = 0
    problems = []
    for t in tasks:
        for p in probes.build(t):
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
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]}).encode()
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
            rows.append({"id": t["id"], "question": t["prompt"], "right_answer": t["reference"], "answer": first,
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
