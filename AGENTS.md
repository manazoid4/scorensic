# Agent instructions: Scorensic

Scorensic checks benchmark **graders**, not models. Offline, deterministic, stdlib-only core.

## Rules
- Evidence before claims. Synthetic fixtures (`examples/`) prove the checks fire on toy graders, nothing more. Never present them as real-benchmark results.
- Every public claim needs a source in `research/evidence.json` with a classification (Verified / Partially verified / Hypothesis).
- Fill the gaps competitors leave (README "Where Scorensic fits"); do not rebuild what evalmut, BenchJack, Harbor or Inspect already do. Credit them.
- Core must run on a Ryzen 4650U / 16 GB laptop, offline, no API key, no GPU. Optional integrations stay optional.
- No runtime dependencies without a written reason in DECISIONS.md. Never copy AGPL code (MiroFish rejected).
- Python graders are not sandboxed: never audit untrusted grader code on the host.
- Responsible disclosure: report grader bugs in live third-party benchmarks to maintainers before publishing details.
- No private data, credentials or the maintainer's location in this public repo.
- Sub-agents: Sonnet for Claude sub-agents; OpenCode (`opencode-go/deepseek-v4.1-flash`) for bounded implementation/test work. Max two cheap workers at once, separate files.

## Workflow
`uv sync` → change → `uv run pytest -q` → `uv run scorensic demo` → update BUILD_STATUS.md + WORK_LOG.md → branch, PR, merge when CI is green.
The public page lives in the separate MazWorkSite repo (`app/research/scorensic`). Update `status.json` here and the page there when the stage changes, only with evidence.
