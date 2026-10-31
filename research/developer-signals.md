# Developer signals (public issues/PRs; checked 2026-10-31)

All were opened and read via the GitHub API unless marked. No X/Twitter posts were retrieved; anything from there is Hypothesis and none is used here.

| Date | Where | What was reported | Class |
|---|---|---|---|
| 2025-09-03 | https://github.com/SWE-bench/SWE-bench/issues/465 (jacobkahn, closed) | Agents run `git log --all` and see future fix commits for SWE-bench Verified instances (pytest-6202, django-13513, django-15572) | Verified |
| 2026-05-17 | https://github.com/SWE-bench/SWE-bench/pull/581 (myz-ah, closed, not merged per API) | Multilingual containers still ship full upstream history, tags, reflog; `git log --all --grep='#4738'` yields gold patch; Python path already cleaned by PR #471 | Verified (current state of fix not checked) |
| 2026-09-01 to 2026-09-16 | https://github.com/UKGovernmentBEIS/inspect_evals/pull/2334 (jkopczyn, merged) | `paws` `includes()` scorer gave 8000/8000 for constant `yesno`; boolq regex accepted "I don't know" on all No items; fix adds shared bad-match list for reuse | Verified |
| 2026-09-21 | https://github.com/harbor-framework/terminal-bench/issues/2037 (jqLi1626, open) | Hosted validation shows success for Oracle reward 2 and Nop reward 0.5 / -1 (should be exactly 1 / 0), with a deterministic repro | Verified |
| 2026-09-25 | https://github.com/harbor-framework/terminal-bench/pull/2097 (stbenjam, open) | Contributor builds "hidden 27 candidates: 6 valid, 21 cheats" harness to test one task's verifier | Verified |
| 2026-08-29 | https://github.com/harbor-framework/terminal-bench/pull/1861 "Harden takens-embedding-lean verifier boundary" (open) | Title only seen via search; body not read | Hypothesis (title-level) |
| 2026-08-15 | https://github.com/harbor-framework/terminal-bench/pull/1602 "fix bun-sourcemap-leak (unenforced constraint)" (open) | Title only seen via search; body not read | Hypothesis (title-level) |
| 2025 | https://github.com/uiuc-kang-lab/agentic-benchmarks (tau-bench) | Do-nothing agent scores 38%; patch released | Verified (README) |

## Reading
- Signals are real, recent and concentrated in Harbor/Terminal-Bench, inspect_evals and SWE-bench. The same two failure shapes recur: (a) grader accepts junk/empty/hedged input, (b) agent-visible environment contains the answer.
- Each was found by a human reading transcripts or reasoning about one task, then fixed with a one-off test. That supports "people hand-build grader unit tests repeatedly"; it does not by itself prove they would adopt a new tool.
- Searched but found nothing: tau-bench empty-response issue (search returned 0 results; the ABC repo documents it instead).
- Counts for user numbers were not available; I did not estimate any.
