# Direction change, 31 Oct 2026 (maintainer decision)

**From:** a technical tool that audits benchmark graders, for benchmark maintainers.
**To:** a simple tool that shows a business owner, in plain English, whether a local AI model can do *their* work, on *their* machine. It builds the trust that local inference needs, and supports Maz Works setting up local models (GPUs, custom configs).

## Why (evidence)
- YC Requests for Startups, Winter 2027 (ycombinator.com/rfs, read 31 Oct 2026):
  - "Own Your Intelligence" (Jon Xu): "there's still a big gap between downloading an open model and owning intelligence that improves a business. Someone has to turn workflows into evals … and carry all of it forward with each new base model."
  - "AI for the air-gapped economy": customers want AI "running entirely inside their own building, with no internet connection"; YC wants on-prem models and deployment tooling.
- What exists today (31 Oct 2026 search):
  - LocalScore (Mozilla Builders) measures *speed* on your hardware, not whether the model does your job.
  - Ollama benchmark apps (e.g. sanyokkua/ollama_llm_bench) are for developers and use an LLM as judge.
  - Small-business guides say "hire a developer for half a day".
  - **Unserved (hypothesis, to verify with real owners):** a non-technical owner proving a local model works on their own tasks before paying for hardware or setup.

## What stays from v0.1
The grader-checking engine becomes the quiet differentiator: "we test the test". Before a business sees a score, Scorensic checks that the marking is honest (rejects wrong and empty answers, accepts valid ones, gives the same result every run). Generic leaderboards and LLM-as-judge tools don't do this.

## Shape of the simple version (proposal)
1. The owner fills in a short sheet of 10–20 real examples: a task and the right answer (invoice totals, booking details, replies to common questions).
2. One command, or double-click, runs them on the local models installed on the machine.
3. They get a one-page report card: how many were right, any made-up facts, speed, "your data never left this computer", and a comparison with the monthly cost of a cloud tool.
4. When a new model comes out, they re-run the same sheet ("carry it forward with each new base model").

## Not yet verified
- That owners want this. That needs 5 conversations before scaling (Mom Test rules).
- UK sovereign AI funding: the scheme, eligibility and amounts are not yet researched. Do not claim them.
