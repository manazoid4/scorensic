# Prior art (checked 2026-10-31)

## Direct prior art for the whole idea
1. **BenchJack** (UC Berkeley RDI; arXiv 2605.12673, 2026-05-12; repo created 2026-04-15, Apache-2.0, 53 stars). Automated hackability audit, 8 flaw classes, 219 flaws across 10 benchmarks, iterative patch loop cut hackable-task ratio from ~100% to <10% on four benchmarks (abstract). LLM-driven (Claude Code/Codex). E02 E03.
2. **BenchProbe** (bettyguo; repo 2026-05-15, last push 2026-06-08, Apache-2.0, 3 stars). Offline static checks, "grades benchmarks, not models", leaderboard. Not run by me. E04.
3. **evalmut** (egnaro9; 2026-08-08, MIT, 4 stars) and **muteval** (AshwinUgale; 2026-06-15, Apache-2.0, 12 stars). Mutation testing for eval graders / suites. E05.
4. **Agentic Benchmark Checklist** (Zhu et al., arXiv 2507.02825, 2025-07-03). Manual checklist + case-study scripts; no general tool. E01.
5. **Harbor Oracle/Nop agents** and the Terminal-Bench authoring flow. E06.

## Related research
- UTBoost, ACL 2025 (test augmentation for SWE-bench). E10, partially verified.
- ImpossibleBench (arXiv 2510.20270, 2025-10-23): mutates tests to target model cheating, not grader quality. E12.
- METR reward-hacking post (2025-06-05). E11.
- MILE mutation framework for LLM in-context learning (arXiv 2409.04831), cited by muteval docs; I did not open it (Hypothesis that it is relevant).
- LLM-judge meta-evaluation, e.g. "Know Thy Judge" (arXiv 2503.04474) seen in search results only, not opened; and an ACM paper on mutation testing LLM semantic judges (DOI 10.1145/3822455.3838768), search snippet only. Both Hypothesis for relevance to deterministic code graders.
- Classical mutation testing (PIT, Stryker, mutmut) referenced by evalmut/muteval READMEs.
- Warning on a source: emergent.sh "Muteval officially launched" page has internally inconsistent dates (published 2026-08-22, says released 2025-01-16) and I treat it as unreliable; I rely on the muteval repo/docs instead.

## Dependency licence and maintenance table (GitHub API + PyPI JSON, 2026-10-31)

| Dependency | Licence | Stars | Last push / release | Notes |
|---|---|---|---|---|
| inspect_ai | MIT (PyPI classifier) | 3,148 | push 2026-10-31; v0.3.287 | Very active; pre-1.0 API churn likely (0.3.x) |
| inspect_evals | MIT | 728 | push 2026-10-30 | 267 open issues |
| harbor | Apache-2.0 | 6,669 | push 2026-10-31 | 1,213 open issues; moving fast |
| terminal-bench | Apache-2.0 | 995 | push 2026-10-30 | repo created 2026-01-25 per API |
| promptfoo | MIT | 26,674 | push 2026-10-31; PyPI wrapper "promptfoo" 0.2.0 2026-09-18 | PyPI package is a thin wrapper; npm is main distribution (not verified) |
| hypothesis | MPL-2.0 (PyPI license_expression; GitHub API says NOASSERTION) | 9,127 | push 2026-10-30; v6.170.14 | MPL-2.0 is file-level copyleft: fine as a dev/runtime dependency, do not copy its files into our tree |
| mutmut | BSD-3-Clause | 1,519 | push 2026-10-28; v3.8.1 | Mutates Python source, not graders' inputs; useful only if we mutate grader code itself |
| simpy | MIT (PyPI classifier) | not retrieved (api path python-simpy/simpy 404; simpy/simpy 404) | v4.1.2 uploaded 2026-05-24 | Discrete-event simulation; no clear role in grader checking (Hypothesis) |
| BenchJack | Apache-2.0 | 53 | push 2026-05-25 | |
| evalmut | MIT | 4 | push 2026-10-25 | |
| muteval | Apache-2.0 | 12 | push 2026-10-04 | |
| MiroFish | AGPL-3.0 | 83,051 | push 2026-10-16 | See verdict |

## MiroFish verdict
Not a fit. README: it ingests seed material (news, reports), builds a GraphRAG, runs thousands of persona agents on simulated social platforms (OASIS engine), and writes a prediction report; needs an LLM API and Zep Cloud. Nothing about benchmarks, graders, scoring or reproducibility. It is AGPL-3.0, which would force network-service source disclosure on derivatives. Its star count (83k) is popularity, not relevance. Skip.
