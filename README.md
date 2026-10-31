# Scorensic

**Making AI agent evaluations more reproducible, transparent and trustworthy.**

`scorensic` checks the *grader* of a benchmark, not the model. It feeds the grader inputs whose correct verdict is already known (the reference answer, valid reformattings, empty output, refusals, known-wrong answers, small mutations of the reference, hedged multi-answer output) and reports every case where the grader disagrees. It also re-runs each input in separate processes to catch nondeterministic scoring, and searches agent-visible files for leaked answers.

> **Status: research and development (v0.1).** The checks work on the bundled synthetic fixtures and are covered by tests. They have **not** yet been validated against real published benchmarks. Nothing here is a certification. See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

## Why

A benchmark score is only as good as the code that marks the answers. Published audits have found graders that pass agents which do nothing, accept answers that merely *contain* the right string, or leak expected outputs into the agent's environment. Sources and their verification status are in [`research/`](research/) and [RESEARCH_EVIDENCE.md](RESEARCH_EVIDENCE.md).

## For businesses: can AI do this job?

Put 10–20 of your real tasks in a sheet (`question,right_answer`, optional `context`). Scorensic runs them on any model, local or online, and gives you a one-page report card. It shows how many were right, wrong answers stated confidently, "didn't know", consistency, speed, and whether your data left the building. Before scoring, it checks that the marking itself can't be fooled.

```bash
uv run scorensic check examples/business/invoices.csv --model llama3.2            # local Ollama
uv run scorensic check my-tasks.csv --model qwen3 --model llama3.2                  # compare models
uv run scorensic check my-tasks.csv --endpoint https://api.example.com/v1 --model x --key-env MY_API_KEY
```

The bundled `examples/business/invoices.csv` is a short, made-up starter sheet. First ready-made pack: [UK complaints handling](packs/uk-complaints/) (54 tasks; spotting complaints, what the customer wants, references, escalation, vulnerability, FCA deadlines).

## For eval builders: check the grader

The rest of this README covers the grader-integrity engine for benchmark maintainers and eval teams.

## Quick start

Needs [uv](https://docs.astral.sh/uv/) (it fetches Python 3.11+ if missing). No API key, no network after install, no GPU.

```bash
git clone https://github.com/manazoid4/scorensic
cd scorensic
uv sync
uv run scorensic doctor
uv run scorensic demo          # audits the 6 synthetic examples, writes results/*.html
uv run pytest                 # reproduces the expected detections
```

Expected demo output (synthetic toy graders, not real benchmarks):

```
01-clean-control       findings=0   (none)
02-substring-grader    findings=4   (accepts_wrong_answer=4)
03-strict-exact        findings=6   (rejects_valid_answer=6)
04-hidden-state        findings=3   (nondeterministic_score=3)
05-leaky-workspace     findings=3   (answer_leak=2, grader_visible=1)
06-do-nothing-passes   findings=15  (accepts_wrong_answer=15)
```

Each fixture contains one deliberate fault, and the test suite asserts that only that fault's check fires. The demo takes about 3.5–5 s and peaks at about 53 MiB of memory, measured across all processes on a Ryzen 5 PRO 4650U laptop.

## Where Scorensic fits

Good tools already exist. Scorensic credits them and targets what they leave open.

| Existing work | Does well | Leaves open | Scorensic |
|---|---|---|---|
| [BenchJack](https://github.com/benchjack/benchjack) | Agent-driven exploit scan of whole benchmarks | Needs Claude Code or Codex; proofs not auto-verified | Offline, deterministic, no model or API key |
| [evalmut](https://github.com/egnaro9/evalmut) | Rigorous mutation testing of grader verdicts (use it for deep analysis) | No repeated-run or cross-process consistency check, no environment leak scan | Re-scores every input across processes; scans agent-visible files |
| Harbor oracle / nop agents | Reference passes, empty agent fails | Its manual: a passing oracle does not prove wrong answers fail | Reusable junk, hedged, mutated and known-wrong answers per task |
| Hand-written fixes ([inspect_evals #2334](https://github.com/UKGovernmentBEIS/inspect_evals/pull/2334), [terminal-bench #2097](https://github.com/harbor-framework/terminal-bench/pull/2097)) | Fix the bug that was found | One-off; the bug class recurs elsewhere | One command, any Python or command grader |

Full matrix and sources: [research/competitors.md](research/competitors.md), [research/verified-gaps.md](research/verified-gaps.md), and an adversarial review of this project in [research/critical-review.md](research/critical-review.md).

## Audit your own grader

An eval directory needs `eval.json` and a JSONL task file:

```json
{
  "name": "my-eval",
  "grader": {"type": "python", "path": "grader.py", "function": "grade"},
  "tasks": "tasks.jsonl",
  "agent_visible": ["workspace"],
  "equivalent_transforms": ["trailing_newline"],
  "repeats": 3,
  "processes": 2,
  "timeout_s": 60,
  "pass_threshold": 1.0
}
```

```jsonl
{"id": "t1", "prompt": "What is 17 + 25?", "reference": "42", "valid_alternatives": ["42.0"], "known_wrong": ["41"]}
```

- **Python grader:** `grade(task: dict, output: str) -> bool | float | {"score": float}`. Runs in a separate `python -I` process.
- **Command grader:** `{"type": "command", "command": ["bash", "test.sh"]}` receives `{"task", "output"}` as JSON on stdin; exit code 0 = pass, or print `{"score": x}`.

```bash
uv run scorensic audit path/to/my-eval --fail-on high     # exit 1 on high-severity findings (CI)
uv run scorensic compare results/baseline.json results/latest.json
uv run scorensic report results/my-eval.json              # re-render HTML
```

## Checks

| Check | Severity | What it means |
|---|---|---|
| `accepts_wrong_answer` | high | A known-wrong, empty, refusing, mutated or hedged output passed |
| `rejects_reference` | high | The task's own reference answer fails its grader |
| `answer_leak` | high | The reference appears verbatim in the prompt or an agent-visible file |
| `grader_visible` | high | Grader code or the task file is inside an agent-visible path |
| `nondeterministic_score` | medium | Identical input scored differently across repeats or processes |
| `rejects_valid_answer` | medium | A listed alternative or harmless reformatting failed |
| `grader_error` | low | The grader raised instead of returning a score |

There is deliberately no single "integrity score": each finding is one concrete input you can rerun.

## Design constraints

Runs on a 6-core laptop with 16 GB RAM, offline, one worker by default, no runtime dependencies beyond the Python standard library. Measured figures are in [BUILD_STATUS.md](BUILD_STATUS.md).

**Safety:** Python graders run in a separate process with a timeout (and a memory limit on Linux/macOS). That is isolation from crashes, not a security sandbox. Only audit grader code you trust, or run inside a container/VM.

## Project files

[ROADMAP.md](ROADMAP.md) · [DECISIONS.md](DECISIONS.md) · [BUILD_STATUS.md](BUILD_STATUS.md) · [docs/methodology.md](docs/methodology.md) · [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md)

Maintained by [Maz Works](https://www.mazworks.uk/research/scorensic) as an independent open-source project. Apache-2.0.
