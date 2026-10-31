"""Adapter fidelity: run the maintainers' own case lists (PR #2334) through each scorer via the adapter."""
import json
from inspect_ai.scorer import includes, pattern
from scorensic.inspect_adapter import grader

BAD = [("yesno", "Yes"), ("yesno", "No"), ("I don't know", "No"), ("Not sure", "No"), ("None of the above", "No"),
       ("I cannot determine the answer.", "No"), ("Yes-man tendencies aside", "Yes"), ("Unlike yesterday", "Yes"),
       ("I like her eyes", "Yes"), ("Domino", "No")]
EXACT = [("Yes", "Yes"), ("yes", "Yes"), ("Yes.", "Yes"), ("**YES!!**", "Yes"), (" Yes\n", "Yes"),
         ("No", "No"), ("no", "No"), ("No.", "No"), ("**NO!!**", "No"), ("(No)", "No"), (" No\n", "No")]
SCORERS = {"paws-prefix": includes(), "paws-postfix": pattern(r"\A\W*\b(Yes|No)\b\W*\Z"),
           "boolq-prefix": pattern(r"(Yes|No).?\Z"), "boolq-postfix": pattern(r"\A[\W_]*(Yes|No)[\W_]*\Z")}
out = {}
for name, sc in SCORERS.items():
    g = grader(sc)
    bad = [c for c, t in BAD if g({"id": "x", "reference": t}, c) == 1.0]
    exact = [c for c, t in EXACT if g({"id": "x", "reference": t}, c) != 1.0]
    out[name] = {"bad_accepted": bad, "valid_rejected": exact}
    print(f"{name:14} bad accepted {len(bad)}/10  valid rejected {len(exact)}/11  {exact}")
json.dump(out, open("../results/fidelity.json", "w"), indent=2)
