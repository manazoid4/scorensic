# Decision

**Recommendation: CONTRIBUTE first, with a small BUILD that is an adapter layer, not a new category. Do not market it as a market gap.**

## Why not plain BUILD
- The headline pitch is already taken: benchmark hackability/leakage (BenchJack, Berkeley RDI, May 2026; BenchProbe), mutation testing of graders (evalmut, muteval), null/oracle checks (Harbor), human audits (Epoch, ABC). See verified-gaps.md "Not gaps".
- No demand data found for a separate tool.

## Why not STOP
- The pain is real and recent (SWE-bench #465/#581, inspect_evals #2334, Terminal-Bench #2037/#2097).
- Every one of those fixes was a hand-written one-off test, and Harbor's own manual says Oracle 1.0 does not prove wrong solutions fail. The reusable fixture-library-plus-adapters slice (G1, G2) looks unserved, though I only read READMEs of evalmut/muteval, not code.
- Competitors are small and young, so cooperation is cheap.

## Why not PIVOT
- Nothing found suggests a better adjacent target. LLM-judge calibration is crowded by platforms (H); model ranking is out of scope by charter.

## Suggested path (cheap, reversible, in this order)
1. **Spike (1-2 days, before writing any tool):** install evalmut and muteval, point each at one Inspect scorer (e.g. paws pre-fix `includes()`) and one Harbor verifier. If either already catches the paws bug with little glue, STOP building and contribute adapters there instead.
2. **If the spike shows a gap:** build the smallest CLI that loads a task's grader through an adapter and runs fixtures: empty, target-echo, negation, hedge, repeat-N determinism, and a cheats/valid pair directory per task. Offline, no LLM. Do not rank models.
3. **Contribute upstream in parallel:** (a) to Harbor/Terminal-Bench, a per-task `cheats/` + `valid_alternatives/` check next to Oracle/Nop (PR 2097 shows demand; also issue 2037 is a small first PR); (b) to inspect_evals, a shared "scorer must reject junk" test helper generalising `YES_NO_BAD_MATCHES`; (c) to BenchJack, verification oracles that confirm PoCs deterministically (its README lists this as missing).
4. **Success measure before scaling:** at least one merged upstream PR or one real grader bug found in a third-party benchmark with a reproducible fixture. Without that, stop.

## Rules to keep us honest
- Say "BenchJack and evalmut exist" in our README.
- Report results as per-benchmark grader findings, never model rankings.
- Use responsible disclosure before publishing any exploit-style finding on a live benchmark (BenchProbe uses 90 days; adopt similar).

## What I did not check (could change the call)
OpenAI Evals, Scale SEAL, Artificial Analysis, Microsoft agent eval tooling, Promptfoo/LangSmith internals (snippets only), inspect_evals contributor docs for an existing scorer-test convention, the Epoch primary pages, the OpenAI SWE-bench Verified page (unreadable by my fetcher), X/Twitter, and any running of competitor tools. If a null-solver or scorer-test feature already exists in Inspect, G1/G5 weaken.
