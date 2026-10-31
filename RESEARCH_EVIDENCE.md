# Key evidence (full list: research/evidence.json)

| Finding | Source | Class |
|---|---|---|
| A do-nothing agent scores 38% on tau-bench airline; Agentic Benchmark Checklist published | arXiv 2507.02825 (Jul 2025) | Verified |
| inspect_evals paws scorer gave full marks to the string "yesno"; fixed with a hand-written bad-answer list | github.com/UKGovernmentBEIS/inspect_evals/pull/2334 (Sep 2026) | Verified |
| SWE-bench agents could read the fix via `git log --all`; Multilingual images reported still leaking | github.com/SWE-bench/SWE-bench/issues/465 (Sep 2025), PR #581 (May 2026) | Verified |
| A contributor hand-built 21 cheats + 6 valid answers to test one Terminal-Bench verifier | github.com/harbor-framework/terminal-bench/pull/2097 (Sep 2026) | Verified |
| BenchJack: LLM-driven scanner for benchmark exploits (Berkeley RDI) | github.com/benchjack/benchjack; arXiv 2605.12673 (May 2026) | Verified |
| evalmut: mutation testing of graders (blind/brittle spots); no cross-process or environment-leak checks found | github.com/egnaro9/evalmut (README + source grep, 31 Oct 2026) | Partially verified |
| Fixing rigid grading moved CORE-Bench from 42% to 95% | anthropic.com/research/demystifying-evals-for-ai-agents | Verified |
| Epoch flagged 9 of 15 benchmarks as flawed | secondary sources only | Partially verified |
