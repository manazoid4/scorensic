"""inspect_evals boolq scorer at 2999eaadad35 (src/inspect_evals/boolq/boolq.py), run via the Scorensic Inspect adapter."""
from inspect_ai.scorer import pattern
from scorensic.inspect_adapter import grader

grade = grader(pattern(r"\A[\W_]*(Yes|No)[\W_]*\Z"))
