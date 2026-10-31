# Roadmap (ordered by value; each item must close a verified gap)

1. **Real validation:** reproduce inspect_evals PR #2334 (paws scorer accepted "yesno") at the pre-fix commit. Report detected / missed honestly.
2. **Inspect AI scorer adapter** (optional extra; core stays stdlib).
3. **Harbor / Terminal-Bench verifier adapter** (command grader over a task dir) + small upstream PR for terminal-bench issue #2037.
4. **git-history leak probe** (SWE-bench #465 class): search `git log --all` of an agent-visible repo for the gold patch.
5. Higher-confidence nondeterminism: adaptive repeats with a stated detection bound.
6. Upstream: offer a "scorer must reject junk" helper to inspect_evals; cross-link evalmut for deep mutation.
