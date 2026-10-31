# Known limitations (v0.1)

1. **No real-benchmark validation yet.** All detections shown are on six synthetic toy graders written to contain one fault each.
2. **Generic probes.** Passing every probe does not prove a grader correct. Mutant and hedged-answer probes assume one correct answer; on open-ended tasks they can be false positives (confidence marked "medium").
3. **Leak search is verbatim text only** over files listed in `agent_visible`. Encoded, paraphrased, image or git-history leaks (e.g. SWE-bench `git log --all`) are not detected yet. References under 4 characters are skipped; in prompts, under 12 (short answers are often listed choices). Skips are listed in each report.
4. **Nondeterminism check is a smoke test**: 2 processes x 3 repeats. A grader that flips rarely (e.g. 1 in 100) will usually pass. Raise `--repeats` for confidence; the report states the run count.
5. **Not a sandbox.** Python graders run in a separate `python -I` process with a timeout (memory limit only on POSIX). Run untrusted graders in a container or VM.
6. **No adapters yet** for Inspect AI scorers, Harbor verifiers or SWE-bench harnesses; graders must be wrapped as a Python function or a command.
7. **Deep output-mutation analysis is out of scope**; evalmut does it more rigorously.
