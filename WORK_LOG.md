# Work log

- 2026-10-31: v0.1 core (probes, audit, worker, HTML/JSON report, compare, CLI), six synthetic fixtures, research pass (19 sources), competitor spike (evalmut/muteval READMEs + source grep). Clean-control false positive found and fixed (prompt-leak threshold). Renamed to Scorensic.
- 2026-10-31: Published github.com/manazoid4/scorensic and the live page mazworks.uk/research/scorensic (MazWorkSite #222). Inspect adapter added. Validation 1 (inspect_evals PR #2334): 2/3 known defect types detected, 0 false findings on the 2 fixed scorers; adapter fidelity matches the PR's own lists. The adapter build took under 1 hour, so the critical review's stop gate was not triggered.
