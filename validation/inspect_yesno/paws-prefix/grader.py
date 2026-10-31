"""inspect_evals paws scorer at ac481c7a7b4f (src/inspect_evals/paws/paws.py), run via the Scorensic Inspect adapter."""
from inspect_ai.scorer import includes
from scorensic.inspect_adapter import grader

grade = grader(includes())
