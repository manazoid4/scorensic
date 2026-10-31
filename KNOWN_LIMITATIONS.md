# Known limitations (v0.1)

1. **One real case study only.** Beyond six synthetic fixtures, Scorensic has been validated on one published bug (inspect_evals PR #2334): 2 of 3 known defect types detected, one missed. That is not a detection rate. See validation/RESULTS.md.
2. **Generic probes.** Passing every probe does not prove a grader correct. Mutant and hedged-answer probes assume one correct answer; on open-ended tasks they can be false positives (confidence marked "medium").
3. **Leak search is verbatim text only** over files listed in `agent_visible`. Encoded, paraphrased, image or git-history leaks (e.g. SWE-bench `git log --all`) are not detected yet. References under 4 characters are skipped; in prompts, under 12 (short answers are often listed choices). Skips are listed in each report.
4. **Nondeterminism check is a smoke test**: 2 processes x 3 repeats. A grader that flips rarely (e.g. 1 in 100) will usually pass. Raise `--repeats` for confidence; the report states the run count.
5. **Not a sandbox.** Python graders run in a separate `python -I` process with a timeout (memory limit only on POSIX). Run untrusted graders in a container or VM.
6. **Adapters:** Inspect AI scorers are supported via `scorensic.inspect_adapter` (validated on one case study). Harbor verifiers and SWE-bench harnesses are not yet; wrap them as a command grader.
7. **Deep output-mutation analysis is out of scope**; evalmut does it more rigorously.
