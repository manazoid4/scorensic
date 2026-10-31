"""Grader worker. Runs as a separate process (python -I _worker.py grader.py func).

Reads {"calls": [{"task": {...}, "output": "..."}], "repeats": N, "memory_mb": M} on stdin,
writes {"results": [[result, ...repeats], ...]} on stdout. A result is a float score or
{"error": "..."}. Kept standalone (no package imports) so -I isolation works.
"""
import importlib.util
import json
import sys


def _limit_memory(mb):
    try:
        import resource  # POSIX only; Windows relies on the parent timeout
    except ImportError:
        return
    if mb:
        limit = mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))


def _to_score(value):
    if isinstance(value, dict):
        value = value.get("score")
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"grader returned {type(value).__name__}, expected bool, number or {{'score': ...}}")


def main():
    grader_path, func_name = sys.argv[1], sys.argv[2]
    req = json.load(sys.stdin)
    result_out, sys.stdout = sys.stdout, sys.stderr  # grader prints must not corrupt the JSON result
    _limit_memory(req.get("memory_mb"))
    sys.path.insert(0, str(__import__("pathlib").Path(grader_path).resolve().parent))
    spec = importlib.util.spec_from_file_location("_maz_grader", grader_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    grade = getattr(module, func_name)
    results = []
    for call in req["calls"]:
        runs = []
        for _ in range(req.get("repeats", 1)):
            try:
                runs.append(_to_score(grade(call["task"], call["output"])))
            except Exception as exc:  # grader bugs are findings, not crashes of the tool
                runs.append({"error": f"{type(exc).__name__}: {exc}"[:300]})
        results.append(runs)
    json.dump({"results": results}, result_out)


if __name__ == "__main__":
    main()
