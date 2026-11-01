"""Business front door, tested against a fake OpenAI-compatible server (no real model needed)."""
import itertools
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from scorensic.check import is_local, load_sheet, mark, parse_rules, rule_failures, run, self_check
from scorensic.cli import main

SHEET = Path(__file__).resolve().parents[1] / "examples" / "business" / "invoices.csv"
FLIP = itertools.cycle(["7pm", "7.30pm"])
REPLIES = {
    "invoice total": lambda: "£1,440.00",            # right (formatting differs)
    "due date": lambda: "14 November 2026",           # right
    "supplier": lambda: "Brightwell Plumbing",        # wrong (incomplete)
    "how many people": lambda: "It could be 5, or 6, or 7.",  # hedge: must be wrong
    "what time": lambda: next(FLIP),                  # inconsistent
    "refund": lambda: "No.",                          # right
    "order number": lambda: "I don't know",           # no answer
    "price per hour": lambda: "45",                   # right (currency sign ignored)
}


class Fake(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        q = body["messages"][-1]["content"].lower()
        reply = next(f() for k, f in REPLIES.items() if k in q)
        out = json.dumps({"choices": [{"message": {"content": reply}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


@pytest.fixture
def endpoint():
    srv = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}/v1"
    srv.shutdown()


def test_report_card_counts(endpoint):
    res = run(SHEET, endpoint, ["fake-model"], repeats=2)
    m = res["models"][0]
    status = {r["id"]: r["status"] for r in m["rows"]}
    assert status == {"1": "right", "2": "right", "3": "wrong", "4": "wrong", "5": "wrong",
                      "6": "right", "7": "no_answer", "8": "right"}
    assert (m["right"], m["wrong"], m["no_answer"], m["total"]) == (4, 3, 1, 8)
    assert m["consistent"] == 7  # the time answer flipped
    assert res["endpoint_is_local"] is True


def test_marking_is_self_checked():
    caught, total, problems = self_check(load_sheet(SHEET))
    assert total > 0 and caught == total and problems == []


def test_mark_rejects_padding_and_hedges():
    t = {"reference": "6"}
    assert mark(t, "6") and mark(t, " 6. ")
    assert not mark(t, "6 or 7") and not mark(t, "") and not mark(t, "The answer is 6 people")


def test_is_local():
    assert is_local("http://localhost:11434/v1") and is_local("http://192.168.1.20:8080/v1")
    assert not is_local("https://api.openai.com/v1")


def test_cli_writes_card(endpoint, tmp_path):
    assert main(["check", str(SHEET), "--endpoint", endpoint, "--model", "fake-model", "--out", str(tmp_path)]) == 0
    page = (tmp_path / "invoices-card.html").read_text(encoding="utf-8")
    assert "4 out of 8 right" in page and "stayed on this network" in page


def test_uk_complaints_pack_marking_is_sound():
    pack = Path(__file__).resolve().parents[1] / "packs" / "uk-complaints" / "pack.csv"
    tasks = load_sheet(pack)
    caught, total, problems = self_check(tasks)
    assert len(tasks) == 54 and caught == total and problems == []


def _rules_task(rules, context=""):
    return {"id": "t", "prompt": "Write the reply.", "context": context, "reference": rules}


def test_rules_marking_needs_every_must_and_no_never():
    t = _rules_task("rules: must=Financial Ombudsman Service; must=six months|6 months; never=[")
    assert mark(t, "You may refer this to the Financial Ombudsman Service within 6 months.")
    assert not mark(t, "You may refer this to the Financial Ombudsman Service.")            # missing a must
    assert not mark(t, "Financial Ombudsman Service, six months. Signed [Your Name]")       # placeholder
    assert not mark(t, "I don't know")
    assert mark(t, "the financial  ombudsman service ... SIX MONTHS")                      # case and spacing


def test_rules_match_whole_words_only():
    t = _rules_task("rules: must=refund; never=no")
    assert not mark(t, "We have refunded you.")    # 'refund' is not the word 'refunded'
    assert mark(t, "We will refund you; we know this was annoying.")   # 'know' does not trip never=no


def test_bad_rules_are_rejected():
    with pytest.raises(ValueError):
        parse_rules("rules: maybe=x")
    with pytest.raises(ValueError):
        parse_rules("rules: never=x")


def test_rules_self_check_catches_echo():
    # A rule set the customer's own message already satisfies would pass a model that just copies it back.
    t = _rules_task("rules: must=4471-B; must=replacement", context="Order 4471-B. Please send a replacement.")
    caught, total, problems = self_check([t])
    assert caught < total and any("(context_echo)" in p for p in problems)


def test_uk_complaints_letters_marking_is_sound():
    tasks = load_sheet(Path(__file__).resolve().parents[1] / "packs" / "uk-complaints" / "letters.csv")
    caught, total, problems = self_check(tasks)
    assert len(tasks) == 8 and caught == total and not problems


def test_rules_card_explains_failures(tmp_path):
    from scorensic.report import card_html
    t = _rules_task("rules: must=leaflet")
    row = {"question": "Q", "right_answer": t["reference"], "answer": "Hello", "status": "wrong", "why": rule_failures(t, "Hello")}
    res = {"sheet": "s.csv", "endpoint_is_local": True, "endpoint_host": "localhost", "repeats": 1,
           "marking_check": {"tricks_caught": 1, "tricks_total": 1, "problems": []},
           "models": [{"model": "m", "right": 0, "wrong": 1, "no_answer": 0, "errors": 0, "total": 1, "consistent": 1,
                       "avg_seconds": 1, "rows": [row]}]}
    assert "missing: leaflet" in card_html(res)
