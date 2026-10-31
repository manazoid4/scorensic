import json
import sys
import time

import pytest

from scorensic.audit import audit


def make_eval(tmp_path, grader_src=None, tasks=None, **spec):
    tasks = tasks or [{"id": "t1", "prompt": "What is 17 + 25?", "reference": "42", "known_wrong": ["41"]}]
    (tmp_path / "tasks.jsonl").write_text("\n".join(json.dumps(t) for t in tasks))
    if grader_src:
        (tmp_path / "grader.py").write_text(grader_src)
    spec.setdefault("grader", {"type": "python", "path": "grader.py"})
    (tmp_path / "eval.json").write_text(json.dumps({"name": "t", "tasks": "tasks.jsonl", **spec}))
    return tmp_path


def checks(report):
    return {f["check"] for f in report["findings"]}


def test_raising_grader_is_reported(tmp_path):
    src = "def grade(task, output):\n    return float(output) == float(task['reference'])\n"
    assert "grader_error" in checks(audit(make_eval(tmp_path, src)))


def test_reference_rejected(tmp_path):
    src = "def grade(task, output):\n    return output == 'something else'\n"
    assert "rejects_reference" in checks(audit(make_eval(tmp_path, src)))


CHECK = "import json, sys\nd = json.load(sys.stdin)\nsys.exit(0 if d['output'].strip() == d['task']['reference'] else 1)\n"


@pytest.mark.parametrize("src,expected", [
    (CHECK, set()),
    ("import sys\nsys.exit(0)\n", {"accepts_wrong_answer"}),  # always-pass verifier
])
def test_command_grader_with_absolute_interpreter(tmp_path, src, expected):
    # Regression: an absolute interpreter path in "command" used to crash audit() (found by tests, fixed).
    (tmp_path / "check.py").write_text(src)
    ev = make_eval(tmp_path, grader={"type": "command", "command": [sys.executable, "check.py"]})
    assert checks(audit(ev, repeats=1, processes=1)) == expected


def test_timeout_does_not_hang(tmp_path):
    src = "import time\ndef grade(task, output):\n    time.sleep(30)\n    return True\n"
    start = time.time()
    report = audit(make_eval(tmp_path, src, timeout_s=1), repeats=1, processes=1)
    assert time.time() - start < 15
    assert "grader_error" in checks(report)


def test_prompt_leak_long_answers_only(tmp_path):
    tasks = [
        {"id": "long", "prompt": "Say: the quick brown fox", "reference": "the quick brown fox"},
        {"id": "short", "prompt": "Answer true or false.", "reference": "false"},
    ]
    src = "def grade(task, output):\n    return output.strip() == task['reference']\n"
    report = audit(make_eval(tmp_path, src, tasks=tasks))
    leaks = [f for f in report["findings"] if f["check"] == "answer_leak"]
    assert [(f["task_id"], f["evidence"]["location"]) for f in leaks] == [("long", "prompt")]
    assert any(s["task_id"] == "short" for s in report["skipped"])
