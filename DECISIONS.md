# Decisions

| Date | Decision | Why | Rejected |
|---|---|---|---|
| 2026-10-31 | Name: Scorensic (was "MAZ Eval Integrity") | Maintainer's choice | — |
| 2026-10-31 | Apache-2.0 licence | Patent grant; compatible with MIT (inspect_ai, promptfoo) and Apache-2.0 (harbor) deps; MPL-2.0 hypothesis is a dev dependency only | MIT (no patent grant), AGPL |
| 2026-10-31 | Stdlib-only core, argparse CLI, hatchling + uv | One-command install, tiny footprint, nothing extra to audit | click/typer, pydantic, SQLite (JSON files are enough for v0.1) |
| 2026-10-31 | Graders run in a separate `python -I` process, batched per process | Crash/timeout isolation and cross-process nondeterminism detection with ~2 process starts per audit | One process per call (slow), in-process (a crash kills the tool) |
| 2026-10-31 | No single "integrity score" | A number hides which input failed; findings are rerunnable inputs | Weighted score |
| 2026-10-31 | Position on competitor gaps, not overlap (maintainer: "the whole point is to be different and fill the gaps") | evalmut (grader mutation), BenchJack (LLM hackability scan), Harbor (oracle/nop) exist. Unserved: offline cross-process nondeterminism, runtime env leak scan, command graders, a reusable junk-answer check across benchmarks, adapters for real graders | Rebuilding mutation testing; ranking models |
| 2026-10-31 | MiroFish rejected | AGPL-3.0 social-simulation engine; unrelated to grader correctness; heavy deps | Integrating it |
| 2026-10-31 | No SimPy / mutmut / promptfoo dependency | Fault injection here is input-level and deterministic; mutmut mutates source code; promptfoo targets prompt evals | — |
| 2026-10-31 | Prompt-leak check only for references >= 12 chars | Clean control produced a false positive: "false" is listed as a choice in its own prompt | Flag all |
