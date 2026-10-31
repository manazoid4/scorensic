# Contributing

1. `uv sync && uv run pytest -q` must pass.
2. A new check needs: a real-world motivating source (link), a synthetic fixture with the fault, a clean control showing no false positive, and tests.
3. Check first whether evalmut, BenchJack, Harbor or Inspect already do it; if so, contribute there.
4. No new runtime dependencies without a DECISIONS.md entry.
5. Grader bugs in live benchmarks: tell the maintainers first (see SECURITY.md).
