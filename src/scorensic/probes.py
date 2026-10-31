"""Probe outputs fed to a grader. Positive probes should pass, negative probes should fail.

Every negative probe is built from the task alone (no model calls), so a run is deterministic.
"""
import re

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
_FLIPS = {"true": "false", "false": "true", "yes": "no", "no": "yes"}


def _norm(text):
    return " ".join(str(text).split()).lower()


def mutants(reference):
    """Small wrong edits of the reference. A good grader should reject each one."""
    ref = str(reference)
    out = []
    m = _NUMBER.search(ref)
    if m:
        num = m.group()
        bumped = str(int(num) + 1) if "." not in num else f"{float(num) + 1:g}"
        out.append(("mutant_number", ref[: m.start()] + bumped + ref[m.end():]))
    flipped = re.sub(r"\b(true|false|yes|no)\b", lambda w: _FLIPS[w.group().lower()], ref, count=1, flags=re.I)
    if flipped != ref:
        out.append(("mutant_boolean", flipped))
    lines = ref.rstrip("\n").split("\n")
    if len(lines) > 1:
        out.append(("mutant_drop_last_line", "\n".join(lines[:-1])))
    elif len(ref.strip()) >= 6:
        out.append(("mutant_truncate", ref.strip()[: len(ref.strip()) // 2]))
    return out


TRANSFORMS = {
    "trailing_newline": lambda s: s + "\n",
    "surrounding_whitespace": lambda s: f"  {s.strip()}  ",
    "case": lambda s: s.swapcase(),
}


def build(task, transforms=("trailing_newline",)):
    """Return probes for one task: dicts with kind, output, expect ('pass'|'fail'), confidence."""
    ref = str(task["reference"])
    valid = [ref] + [str(a) for a in task.get("valid_alternatives", [])]
    valid_norm = {_norm(v) for v in valid}
    probes = [{"kind": "reference", "output": ref, "expect": "pass", "confidence": "high"}]
    for alt in task.get("valid_alternatives", []):
        probes.append({"kind": "valid_alternative", "output": str(alt), "expect": "pass", "confidence": "high"})
    for name in transforms:
        probes.append({"kind": f"equivalent_{name}", "output": TRANSFORMS[name](ref), "expect": "pass", "confidence": "high"})

    negatives = [
        ("empty", "", "high"),
        ("whitespace_only", " \n", "high"),
        ("refusal", "I don't know.", "high"),
        ("prompt_echo", str(task.get("prompt", "")), "medium"),
        # Several candidates with the right one buried in the middle: catches substring/"contains" graders.
        ("hedged_answer", f"It could be {_decoy(ref)}, or {ref}, or {_decoy(ref, 2)}.", "medium"),
    ]
    negatives += [(f"known_wrong_{i}", str(w), "high") for i, w in enumerate(task.get("known_wrong", []))]
    negatives += [(kind, text, "medium") for kind, text in mutants(ref)]
    seen = set()
    for kind, text, conf in negatives:
        # Never call something wrong if it is (a normalised form of) an accepted answer.
        if _norm(text) in valid_norm or (kind != "empty" and not text.strip() and kind != "whitespace_only"):
            continue
        if text in seen:
            continue
        seen.add(text)
        probes.append({"kind": kind, "output": text, "expect": "fail", "confidence": conf})
    return probes


def _decoy(ref, step=1):
    muts = [t for _, t in mutants(ref)]
    if muts:
        return muts[0] if step == 1 else muts[0] + "0"
    return f"not {ref}" if step == 1 else "something else"
