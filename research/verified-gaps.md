# Verified gaps (and gaps that are NOT gaps)

Date of check: 2026-10-31. Method: web research only; I installed and ran nothing.

## Not gaps (already covered; do not claim these)
| Claim | Covered by | Evidence |
|---|---|---|
| "Nobody checks benchmarks for hackability / answer leakage" | BenchJack (LLM-driven), BenchProbe (static), ABC (manual) | E02 E03 E04 E01 |
| "Nobody does mutation testing of graders" | evalmut, muteval | E05 |
| "Task authors have no null-agent / oracle check" | Harbor Nop + Oracle in Terminal-Bench CI | E06 |
| "Nobody audits benchmarks for broken graders" | Epoch Benchmark Reviews (manual, secondary-source only) | E14 |
| "Nobody tests LLM judges" | LangSmith Align Evals etc. (H) | E17 |

## Candidate gaps (each is narrow; classification says how sure)
| # | Gap | Why I think it exists | Class |
|---|---|---|---|
| G1 | No tool runs a benchmark's real grader (Inspect scorer, Harbor verifier, SWE-bench harness) against a reusable fixture library: empty, target-echo, negated, hedged, wrong-but-plausible, and known-valid alternatives, offline and deterministically. | evalmut/muteval work on their own `EvalCase`/config abstraction; Harbor's own manual says Oracle 1.0 does not prove wrong solutions fail; PR 2097 and inspect_evals PR 2334 hand-build exactly these lists. I did not read evalmut/muteval source to confirm they cannot wrap Inspect/Harbor. | Partially verified |
| G2 | Valid-alternative acceptance (false negatives: "96.12" vs "96.124991") is rarely tested. | Anthropic post documents CORE-Bench 42% to 95% from rigid grading; evalmut has a "brittle spot" operator so it is not unique. | Partially verified |
| G3 | Repeat-run determinism check for graders (same input, N runs, same verdict). | Harbor manual advises running Oracle twice; Anthropic mentions stochastic tasks. I found no tool that automates it. | Hypothesis |
| G4 | Environment leakage check as a runtime probe (search agent-visible filesystem/git for gold strings) rather than static pattern or LLM audit. | SWE-bench #465 and PR 581 are exactly this and were found manually; BenchJack V2 does it with an LLM; BenchProbe statically. A cheap deterministic probe may be unserved. | Hypothesis |
| G5 | Integration: a check that plugs into Inspect and Harbor CI so authors get it for free. | Inspect and Harbor both have contributor flows; none mentioned grader mutation tests in what I read. | Hypothesis |

## Honest size of the gap
- Real, repeated, recent pain (Verified): graders that accept junk or leak answers. Seen in SWE-bench, inspect_evals, Terminal-Bench, tau-bench.
- Unverified: that anyone wants a *new standalone* tool rather than extending BenchJack/evalmut/Harbor. No user-demand data was found (no download counts, no issue asking for such a tool).
- Competitors are all young and tiny (3-53 stars), so none has locked the space; this is an argument for contributing or building small, not for claiming white space.
