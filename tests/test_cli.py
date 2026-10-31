import copy
import json
from pathlib import Path

from scorensic.cli import main
from scorensic.report import html

EX = Path(__file__).resolve().parents[1] / "examples"


def test_demo_writes_reports(tmp_path):
    assert main(["demo", "--out", str(tmp_path)]) == 0
    assert len(list(tmp_path.glob("*.html"))) == 6


def test_fail_on_high(tmp_path):
    assert main(["audit", str(EX / "02-substring-grader"), "--out", str(tmp_path), "--fail-on", "high"]) == 1
    assert main(["audit", str(EX / "01-clean-control"), "--out", str(tmp_path), "--fail-on", "high"]) == 0


def test_compare(tmp_path):
    main(["audit", str(EX / "02-substring-grader"), "--out", str(tmp_path)])
    base = tmp_path / "02-substring-grader.json"
    assert main(["compare", str(base), str(base)]) == 0
    report = json.loads(base.read_text(encoding="utf-8"))
    worse = copy.deepcopy(report)
    worse["findings"].append({**report["findings"][0], "id": "new000000000"})
    (tmp_path / "worse.json").write_text(json.dumps(worse))
    assert main(["compare", str(base), str(tmp_path / "worse.json")]) == 1


def test_html_escapes_grader_output(tmp_path):
    main(["audit", str(EX / "02-substring-grader"), "--out", str(tmp_path)])
    report = json.loads((tmp_path / "02-substring-grader.json").read_text(encoding="utf-8"))
    report["findings"][0]["evidence"]["output"] = "<script>alert(1)</script>"
    page = html(report)
    assert "<script>" not in page and "&lt;script&gt;" in page
