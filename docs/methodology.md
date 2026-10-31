# Methodology

A grader is treated as a function `verdict = grade(task, output)`. For each task Scorensic builds **probes**: outputs whose correct verdict is known from the task alone.

- **Must pass:** the reference; listed `valid_alternatives`; declared `equivalent_transforms` of the reference (default: trailing newline).
- **Must fail:** empty, whitespace, a refusal, the prompt echoed back, a hedged answer listing the reference among decoys, each `known_wrong`, and small mutants of the reference (number +1, true/false flip, truncation, dropped last line). Any must-fail probe whose normalised text equals an accepted answer is dropped.

Each probe is graded `repeats` times in each of `processes` separate processes. If results differ, the probe is reported as `nondeterministic_score` and not used for pass/fail findings. Otherwise a disagreement with the expected verdict is a finding with the exact input, scores and run count.

Leakage: verbatim search for each reference in the prompt (12+ chars) and in files under `agent_visible` (4+ chars); grader and task files inside `agent_visible` are flagged.

**What a finding means:** on this exact input, the grader's verdict contradicts the task's own definition of correct. **What no findings means:** only that these probes passed.

The synthetic fixtures in `examples/` each contain one deliberate fault, plus a clean control, so detection and false-positive behaviour can be reproduced. They are not evidence about any real benchmark.
