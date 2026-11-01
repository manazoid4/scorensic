# Build status (1 Nov 2026)

## Done (with evidence)
- [x] Core CLI: `doctor`, `demo`, `audit`, `report`, `compare` (stdlib only).
- [x] Python and command graders; separate-process execution with timeouts.
- [x] Six synthetic fixtures: every deliberate fault is detected, and the clean control has 0 findings. `uv run pytest -q`: 23 tests (22 passed, 1 skipped without the inspect extra).
- [x] Measured on a Ryzen 5 PRO 4650U with 16 GB RAM, Windows 11, Python 3.15: the demo takes 3.4–4.8 s wall time and peaks at 53 MiB summed RSS across the process tree (3 runs, psutil).
- [x] Research pass (19 sources) and an adversarial review in `research/`.
- [x] Inspect AI adapter (`scorensic[inspect]`). Validation 1 on the real inspect_evals PR #2334 scorers: paws bug detected; boolq false-accept missed; boolq valid-format rejection detected; 0 findings on both fixed scorers. See validation/RESULTS.md.
- [x] Second bug found by the OpenCode test worker and fixed: a grader `print()` corrupted the worker's JSON output.
- [x] Bug found by tests and fixed: an absolute interpreter path in a command grader used to crash `audit()`.

- [x] Business `check` front door + UK complaints pack (54 extraction tasks).
- [x] Rules marking for written work (`rules: must=...; never=...`), self-checked with drop-a-must, add-a-never, prompt-echo and context-echo probes. Letters pack: 8 replies, 118/118 tricks rejected. 34 tests pass, 1 skipped.
- [x] First real-model run (1 Nov, llama3.2:3b + qwen2.5:3b on CPU Ollama): see validation/FIRST-REAL-RUN.md.

## Next (resumable checklist)
- [ ] Business pack: run on bigger local models (qwen3 8B, llama3.1 8B) and one cloud model for comparison; add a "deadline by code" baseline.
- [ ] Ask 3 UK complaints/ops people whether this report card would change a buying decision (no customers yet).
- [ ] Update the live page mazworks.uk/research/scorensic to the business-first message (MazWorkSite repo).
- [ ] Holdout validation: inspect_evals #2310 (agentic_misalignment), #2312 (agentharm). Untouched so far. Measure before changing probes.
- [ ] Refusal variants without punctuation (would fix the boolq miss). Only after the holdout run.
- [ ] Measure false positives on 20–30 known-good graders.
- [ ] Harbor verifier adapter, and a PR for terminal-bench issue #2037.
- [ ] git-history leak probe (SWE-bench #465 class).

## Blocked
- Nothing blocked. Do not claim a detection rate until the holdout and the false-positive runs are done.
