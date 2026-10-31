# Adversarial review of Scorensic (2026-10-31)

Tags: V = Verified (I read code or ran it), P = Partially verified, H = Hypothesis.
Checked: read src/scorensic/{probes,audit,_worker}.py (551 lines incl. cli/report), ran `scorensic demo` (6 fixtures, 0.5-1.1 s each), read the evalmut README (egnaro9/evalmut, 105 commits, last commit Oct 25 2026), two web searches. I did NOT run evalmut, Inspect, or Harbor.

## 1. Unsolved problem, or trivially done already?
- Each check individually is cheap and mostly exists in some form. (P)
  - Reference-must-pass and null-agent-must-fail: Harbor Oracle + Nop (prior research E06). Scorensic's `do-nothing-passes` fixture is Nop reimplemented on a toy.
  - Nondeterminism: Inspect's `epochs` re-runs the *solver* and reduces scores; it does not re-score a fixed output, so it does not test the grader (H: I did not read the Inspect source this session; the search returned only tutorial pages). The honest claim is "nobody automates re-scoring a frozen output across fresh processes". That is a ~10-line loop, not a product.
  - Junk-answer rejection: inspect_evals PR #2334 shows maintainers fixed it with a shared bad-match list. That is the whole "feature".
- The research's own G3/G4/G5 are labelled Hypothesis, and nothing in this review upgrades them. No user demand evidence exists (decision.md admits it). (V)
- The demo fixtures were written by the tool's author to trip the tool's probes: substring grader vs. hedged probe, exact-match vs. whitespace probe, `random()` vs. repeat probe, answer file in `agent_visible`. 6/6 detections is circular. (V)

## 2. Would a maintainer use a separate tool vs. a 20-line pytest?
- Strongest STOP: a maintainer who cares writes `for bad in ["", " ", "I don't know", prompt]: assert not grade(task, bad)` in the repo's existing CI; a maintainer who doesn't care will not install a third-party auditor, and the SWE-bench / paws / Terminal-Bench fixes were all hand-written one-offs by maintainers who already cared. The value of a pytest is that it encodes *task-specific* wrong answers (PR 2097's 27 hidden cases); generic probes are the part that gives the least information. (P)
- The input format is the adoption killer: you must author `eval.json` + `tasks.jsonl` with `reference`, `prompt`, `agent_visible`. Real benchmarks (Inspect `Task`, Harbor `tests/test.sh` + Docker, SWE-bench harness) are not in this shape. Python graders must have signature `grade(task, output)`. No Inspect scorer takes that signature (they take `TaskState, Target`). So "audit a real benchmark" needs an adapter that does not exist, and that adapter is the actual product. (V: only `python`/`command` types in audit.py)
- Command graders: exit code 0 = pass. Real Harbor verifiers write a reward file and run inside a container with the agent's workspace; stdin-JSON does not map. (V/P)

## 3. Is "contribute to evalmut/Harbor/inspect_evals" strictly better?
- Not strictly. evalmut is a single-author, 4-star project built on the author's own `gradecore`; its README scopes it to LLM-app eval cases (P, README only). Upstreaming into a solo project makes you dependent on one maintainer's roadmap; but it is also the cheapest way to get a real user. Harbor and inspect_evals are much larger and have real review capacity.
- Better ordering: do not build more; contribute the *one* thing with a real maintainer-visible bug (Harbor #2037 reward 2 / 0.5 accepted; inspect_evals junk-answer helper). A merged PR is the only evidence of demand the project has.
- Extending evalmut with cross-process rescoring is a few dozen lines if its runner allows it (H, did not read runner.py). That is cheaper than maintaining a parallel tool.

## 4. Code and methodology flaws (all V from reading code)
Probes
- `mutant_number` bumps first number by 1. Any tolerance grader (abs_tol 1, relative 5%, "within 10") correctly accepts it and is flagged `accepts_wrong_answer` (confidence "medium"). Same for numeric `96.12` vs `97.12` when tolerance is legitimately wide.
- `mutant_truncate` (half the reference) and `mutant_drop_last_line` will be accepted by any similarity/ROUGE/F1/embedding grader by design. The limitation text covers "single correct answer" but findings are still `severity=high` in SEVERITY.
- `hedged_answer` ("It could be X, or REF, or Y"): for multi-answer / list / "answer contains the key phrase" tasks the contains-grader is the intended behaviour. Also `_decoy` for non-numeric, non-boolean refs is `"not "+ref`, which *contains* the reference, so any contains-based grader is flagged even when the real flaw is none. Mixed-case and multi-line references are handled by string tricks only.
- `prompt_echo` is `medium` confidence but fails with severity high; if the prompt legitimately contains the answer-format string, it flags a correct grader. When `prompt` is missing it is `""` and silently deduped with `empty`.
- `case` transform exists but is off by default; "equivalent" probes only test trailing newline by default, so "rejects_valid_answer" recall is nearly nil unless the maintainer lists alternatives (and then they already know the issue).
- Probes use Python `str`. Non-string outputs (JSON, code patches, tool traces, files) are not representable. Real agentic benchmarks (the paper-motivating cases) grade world state, not a string. This is the largest scope gap.

Leak heuristic
- Purely verbatim, case-sensitive substring over files the *user declares* in `agent_visible`. The user must already know the visible surface, which is the hard part. It cannot find SWE-bench #465 (git history), which the research cites as motivation; limitation 3 admits it, but the pitch says "scans for leaks".
- No word boundary: a 4-char reference like `true`/`Paris`/`1990` matches inside any visible file. Skipping <4 chars only partly helps; expect high false-positive rates for short answers (listed as "medium").
- Reads files as utf-8 with `errors="ignore"` up to 1 MB; binary, compressed, base64, notebooks, images are unscanned. Cross-task leakage (task A's answer in task B's prompt) is flagged as a leak even when it is just another question.

Isolation
- "Not a sandbox" is correct, and worse than it reads: the worker runs the grader in the same process as the grading loop, with `cwd=eval_dir`, so a grader that writes/deletes files modifies the audited repo. `RLIMIT_AS` is POSIX only; on this Windows machine memory_mb is silently ignored. `-I` isolates the interpreter, not the grader's imports (`sys.path.insert(0, grader_dir)` runs arbitrary code from the benchmark). Auditing third-party benchmarks (the use case) therefore executes untrusted code on the maintainer's host. The README line "only audit graders you trust" defeats the third-party use case. (V)
- Command-grader errors (non-zero exit from a crash) are scored 0.0, so a crashing grader makes every "fail" probe pass quietly and the reference probe produce `rejects_reference`: not distinguishable from legit rejection. `grader_error` only works for the python path.

Nondeterminism design
- 2 processes x 3 repeats = 6 identical-input runs per probe. If a grader is flaky at rate p, P(detect) = 1-(1-p)^6 (roughly, ignoring correlation): p=0.05 gives ~26%, p=0.01 ~6%. Real flakiness (timeouts under load, network, file races, ordering) is usually low-p and load-correlated, which a sequential lightweight run does not reproduce. Flaky findings are reported high confidence on a zero-false-negative-claim basis, but a clean result means little.
- All repeats in a process share state (good for cache bugs, bad for isolating); processes run sequentially, not concurrently, so races never fire. PYTHONHASHSEED varies per process by default so dict/set ordering bugs are the main thing it will really catch.
- `distinct` compares exact JSON of floats; any grader returning float noise (1e-16) is "nondeterministic" even if the pass/fail verdict is stable. (V)

## 5. Does the synthetic demo prove anything?
- No. It proves the code runs and that the probes catch graders written to be caught. Six fixtures, all by the author, one grader each, <1 s runtimes, no real benchmark, no false-positive rate measured on a known-good grader beyond a single clean control (`01-clean-control`, itself written by the author).
- Minimum before any public claim (in order):
  1. Pre-fix inspect_evals paws (PR #2334): write the ~20-line adapter, show Scorensic flags `yesno` and *does not* flag the post-fix scorer. Bug exists and is public, so this is reproducible.
  2. False-positive sweep: run the generic probes on 20-30 *known-good* graders (GSM8K numeric, MATH sympy equivalence, HumanEval pass@1 style, a tolerance-based one) and report how many generate false findings. I predict tolerance/numeric/similarity graders flood with `mutant_number`/`mutant_truncate`.
  3. Cross-check against evalmut on the same tasks: report what Scorensic finds that evalmut does not, and vice versa.
  4. One Harbor task with a real verifier (and Nop/Oracle) reproduced.
- Until then, say "prototype" and quote counts only from real runs.

## 6. Verdict: CONTRIBUTE (with a hard STOP gate on building)
The direction in decision.md is right, but only the contribute half; the narrowed-pitch "pre-flight" CLI is not yet justified by evidence. Do not spend more on the CLI. Three highest-value actions:
1. Run the paws pre-fix reproduction (minimum viable real validation). If it takes more than a day to write the adapter, that is itself the answer: STOP the standalone tool.
2. Open Harbor #2037 PR (and inspect_evals shared "scorer must reject junk" helper) as the demand test. A merged PR is the success criterion; no merged PR in ~3 weeks => STOP.
3. File an evalmut issue/PR for "cross-process rescoring + command graders" instead of maintaining parallel code; fix probe false-positives (tolerance-aware mutants, word-boundary leak matching, float-noise tolerance) only if step 1 shows the tool surfaces something real.

Not checked: evalmut and Harbor internals (did not run them), Inspect `epochs` source semantics, actual download/usage numbers, Windows CRLF effects on probes.
