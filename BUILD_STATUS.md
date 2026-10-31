# Build status (31 Oct 2026)

## Done (with evidence)
- [x] Core CLI: `doctor`, `demo`, `audit`, `report`, `compare` (stdlib only).
- [x] Python and command graders; separate-process execution with timeouts.
- [x] Six synthetic fixtures: every deliberate fault is detected, and the clean control has 0 findings. `uv run pytest -q`: 21 passed.
- [x] Measured on a Ryzen 5 PRO 4650U with 16 GB RAM, Windows 11, Python 3.15: the demo takes 3.4–4.8 s wall time and peaks at 53 MiB summed RSS across the process tree (3 runs, psutil).
- [x] Research pass (19 sources) and an adversarial review in `research/`.
- [x] Bug found by tests and fixed: an absolute interpreter path in a command grader used to crash `audit()`.

## Next (resumable checklist)
- [ ] Reproduce inspect_evals PR #2334 (paws scorer accepts "yesno") at the pre-fix and post-fix commits. Gate: if the adapter takes more than a day, stop the standalone tool and contribute upstream instead.
- [ ] Inspect AI scorer adapter (optional extra).
- [ ] Measure false positives on 20–30 known-good graders.
- [ ] Harbor verifier adapter, and a PR for terminal-bench issue #2037.
- [ ] git-history leak probe (SWE-bench #465 class).

## Blocked
- Nothing blocked. A real-benchmark claim needs the paws reproduction first.
