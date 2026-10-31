"""Builds the inspect_evals yes/no validation cases (PR #2334). Run: python build.py"""
import json
from pathlib import Path

HERE = Path(__file__).parent
PRE, POST = "ac481c7a7b4fb05d6befdfea59b47fc61b839a4f", "2999eaadad35edebada59bac4a687793c11d1c3c"
PAWS_T = "\nAnswer Yes if the following two sentences are paraphrases. If they are not, answer No.\nDo not give any other answer other than Yes or No in your response.\n{prompt}\n"
BOOLQ_T = "\nGiven a passage, answer the subsequent question with either Yes or No. Include nothing else in your response.\n\nPassage: {passage}\n\nQuestion: {question}\n"
# Valid forms per the maintainers' YES_NO_EXACT_MATCHES (tests/utils/case_lists.py @ POST). Used only as "must pass".
VALID = {"Yes": ["yes", "Yes.", "**YES!!**", " Yes\n", "(Yes)"], "No": ["no", "No.", "**NO!!**", " No\n", "(No)"]}
PAWS = [  # sentence pairs written for this test, not taken from the dataset
    ("The bridge was built in 1932 and opened a year later.", "Built in 1932, the bridge opened the following year.", "Yes"),
    ("She moved from Leeds to Bristol in 2010.", "She moved from Bristol to Leeds in 2010.", "No"),
    ("The film was directed by Ana Ruiz and produced by Tom Hale.", "Tom Hale produced the film, which Ana Ruiz directed.", "Yes"),
    ("The river flows north into the lake.", "The lake flows north into the river.", "No"),
]
BOOLQ = [
    ("Mercury is the planet closest to the Sun.", "is mercury the closest planet to the sun", "Yes"),
    ("Penguins are flightless birds found mostly in the Southern Hemisphere.", "can penguins fly", "No"),
    ("The Thames flows through London before reaching the North Sea.", "does the thames flow through london", "Yes"),
    ("Glass is an amorphous solid at room temperature.", "is glass a liquid at room temperature", "No"),
]
SCORERS = {
    "paws-prefix": ("includes()", "from inspect_ai.scorer import includes", PRE, "paws"),
    "paws-postfix": (r'pattern(r"\A\W*\b(Yes|No)\b\W*\Z")', "from inspect_ai.scorer import pattern", POST, "paws"),
    "boolq-prefix": (r'pattern(r"(Yes|No).?\Z")', "from inspect_ai.scorer import pattern", PRE, "boolq"),
    "boolq-postfix": (r'pattern(r"\A[\W_]*(Yes|No)[\W_]*\Z")', "from inspect_ai.scorer import pattern", POST, "boolq"),
}


def task(i, prompt, label):
    return {"id": f"{i}-{label.lower()}", "prompt": prompt, "reference": label, "valid_alternatives": VALID[label],
            "known_wrong": ["No" if label == "Yes" else "Yes"]}


tasks = {
    "paws": [task(i, PAWS_T.format(prompt=f"{a}\n{b}"), y) for i, (a, b, y) in enumerate(PAWS)],
    "boolq": [task(i, BOOLQ_T.format(passage=p, question=q), y) for i, (p, q, y) in enumerate(BOOLQ)],
}
for name, rows in tasks.items():
    (HERE / f"{name}_tasks.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
for name, (expr, imp, commit, ev) in SCORERS.items():
    d = HERE / name
    d.mkdir(exist_ok=True)
    (d / "grader.py").write_text(
        f'"""inspect_evals {ev} scorer at {commit[:12]} (src/inspect_evals/{ev}/{ev}.py), run via the Scorensic Inspect adapter."""\n'
        f"{imp}\nfrom scorensic.inspect_adapter import grader\n\ngrade = grader({expr})\n", encoding="utf-8")
    spec = {"name": f"inspect_evals-{name}", "description": f"inspect_evals {ev} scorer {expr} at commit {commit}",
            "grader": {"type": "python", "path": "grader.py"}, "tasks": f"../{ev}_tasks.jsonl"}
    (d / "eval.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
print("built", list(SCORERS))
