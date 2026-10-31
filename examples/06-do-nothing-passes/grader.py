"""Deliberately faulty: passes unless the output contains a known-wrong answer.

Synthetic analogue of graders that check "nothing bad happened" (e.g. an unchanged
database) rather than "the task was done", so an agent that does nothing passes.
"""


def grade(task, output):
    return not any(w.lower() in output.lower() for w in task.get("known_wrong", []))
