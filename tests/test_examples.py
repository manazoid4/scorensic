"""Each synthetic fixture has one documented fault; the clean control must stay clean."""
from pathlib import Path

import pytest

from scorensic.audit import audit

EX = Path(__file__).resolve().parents[1] / "examples"
EXPECTED = {
    "01-clean-control": set(),
    "02-substring-grader": {"accepts_wrong_answer"},
    "03-strict-exact": {"rejects_valid_answer"},
    "04-hidden-state": {"nondeterministic_score"},
    "05-leaky-workspace": {"answer_leak", "grader_visible"},
    "06-do-nothing-passes": {"accepts_wrong_answer"},
}


@pytest.mark.parametrize("name,checks", sorted(EXPECTED.items()))
def test_fixture_triggers_only_its_fault(name, checks):
    report = audit(EX / name)
    assert {f["check"] for f in report["findings"]} == checks


def test_substring_grader_caught_by_hedge():
    kinds = {f["evidence"]["probe_kind"] for f in audit(EX / "02-substring-grader")["findings"]}
    assert "hedged_answer" in kinds


def test_do_nothing_agent_passes_is_caught():
    kinds = {f["evidence"]["probe_kind"] for f in audit(EX / "06-do-nothing-passes")["findings"]}
    assert {"empty", "refusal"} <= kinds


def test_audit_is_deterministic():
    a, b = (audit(EX / "04-hidden-state") for _ in range(2))
    assert [f["id"] for f in a["findings"]] == [f["id"] for f in b["findings"]]
