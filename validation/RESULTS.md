# Validation 1: inspect_evals yes/no scorers (PR #2334)

**Date:** 31 Oct 2026 · **Scorensic:** 0.1.0 + Inspect adapter · **inspect_ai:** 0.3.287 · **Python:** 3.12 · Windows 11, Ryzen 5 PRO 4650U

## What was tested
These are the real scorer definitions from [inspect_evals PR #2334](https://github.com/UKGovernmentBEIS/inspect_evals/pull/2334), merged 16 Sep 2026:

| Case | Scorer | Commit |
|---|---|---|
| paws-prefix | `includes()` | `ac481c7` (before the fix) |
| paws-postfix | `pattern(r"\A\W*\b(Yes\|No)\b\W*\Z")` | `2999eaa` (after the fix) |
| boolq-prefix | `pattern(r"(Yes\|No).?\Z")` | `ac481c7` |
| boolq-postfix | `pattern(r"\A[\W_]*(Yes\|No)[\W_]*\Z")` | `2999eaa` |

Each scorer is called through `scorensic.inspect_adapter`, not reimplemented. Prompts use the real task templates. The 4 + 4 sentence pairs and passages are written for this test, so no dataset download is needed. The "must pass" forms come from the maintainers' `YES_NO_EXACT_MATCHES`. Their `YES_NO_BAD_MATCHES` list was **not** given to Scorensic. It is used only to score the adapter's fidelity below.

Reproduce:

```bash
cd validation && uv venv --python 3.12 .venv && uv pip install --python .venv inspect_ai==0.3.287 -e ..
.venv/Scripts/python inspect_yesno/build.py     # (bin/python on Linux/macOS)
.venv/Scripts/scorensic audit inspect_yesno/paws-prefix --out results   # etc.
.venv/Scripts/python inspect_yesno/fidelity.py
```

## Adapter fidelity (does it reproduce the PR's own claims?)
| Scorer | Bad answers accepted (of 10) | Valid answers rejected (of 11) |
|---|---|---|
| paws-prefix | 10 | 0 |
| paws-postfix | 0 | 0 |
| boolq-prefix | 4 | 4 (`**YES!!**`, ` Yes\n`, `**NO!!**`, ` No\n`) |
| boolq-postfix | 0 | 0 |

This matches the PR description. The before-fix scorers are broken, and the after-fix scorers pass the maintainers' own test lists.

## Scorensic results (generic probes, no knowledge of the bad list)
| Scorer | Known defect type | Scorensic | Findings |
|---|---|---|---|
| paws-prefix | Accepts wrong or hedging answers (substring match) | **Detected** | 10 `accepts_wrong_answer`: "I don't know." on every No item (the PR reports 4464/8000 such items), hedged multi-answers, prompt echo |
| boolq-prefix | Accepts "I don't know" etc. on No items | **Missed** | The refusal probe ends with a full stop ("I don't know."), so `.?\Z` does not match it. No other probe hit this. |
| boolq-prefix | Rejects valid formats (" Yes\n", "**YES!!**") | **Detected** | 12 `rejects_valid_answer` (the maintainers' post-fix tests require these forms to pass) |
| paws-postfix | none (fixed) | **0 findings** | clean |
| boolq-postfix | none (fixed) | **0 findings** | clean |

**Summary:** 2 of 3 known defect types detected, and 0 findings on the 2 fixed scorers. Runtime is about 13 s per scorer for 76–80 probes × 6 runs, most of it starting Inspect.

## What this does and does not show
- It shows the adapter runs real Inspect scorers unchanged, and that generic probes can catch a real, published scorer bug with no knowledge of it.
- It does **not** show general detection rates. That would need many more scorers, and 3 defect types are far too few for a rate or a confidence interval.
- The boolq miss is a real limitation. The obvious fix is to add refusal variants without punctuation, but that would be tuned on this case. It must be measured on a holdout first: the open issues inspect_evals #2310 (agentic_misalignment) and #2312 (agentharm), which were not looked at before this run.
