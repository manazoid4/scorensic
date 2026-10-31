"""inspect_evals boolq scorer at ac481c7a7b4f (src/inspect_evals/boolq/boolq.py), run via the Scorensic Inspect adapter."""
from inspect_ai.scorer import pattern
from scorensic.inspect_adapter import grader

grade = grader(pattern(r"(Yes|No).?\Z"))
