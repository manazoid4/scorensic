"""Run a real Inspect AI scorer as a Scorensic grader. Optional: needs `inspect_ai` installed.

Grader file example:
    from inspect_ai.scorer import includes
    from scorensic.inspect_adapter import grader
    grade = grader(includes())

The scorer sees a TaskState whose final model output is the probe text and a Target built
from the task's `target` (or `reference`). CORRECT -> 1.0, anything else -> its numeric value or 0.0.
"""
import asyncio


def grader(scorer):
    from inspect_ai.model import ChatMessageAssistant, ChatMessageUser, ModelName, ModelOutput
    from inspect_ai.scorer import CORRECT, Target
    from inspect_ai.solver import TaskState

    def grade(task, output):
        prompt = str(task.get("prompt", ""))
        model = "scorensic/probe"
        state = TaskState(
            model=ModelName(model), sample_id=task["id"], epoch=1, input=prompt,
            messages=[ChatMessageUser(content=prompt), ChatMessageAssistant(content=output)],
            output=ModelOutput.from_content(model, output), choices=task.get("choices"),
        )
        score = asyncio.run(scorer(state, Target(task.get("target", task["reference"]))))
        value = score.value
        if value == CORRECT:
            return 1.0
        return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0

    return grade
