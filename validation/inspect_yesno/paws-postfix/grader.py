"""inspect_evals paws scorer at 2999eaadad35 (src/inspect_evals/paws/paws.py), run via the Scorensic Inspect adapter."""
from inspect_ai.scorer import pattern
from scorensic.inspect_adapter import grader

grade = grader(pattern(r"\A\W*\b(Yes|No)\b\W*\Z"))
