"""Deliberately faulty: substring match. Any output mentioning the reference passes."""


def grade(task, output):
    return task["reference"].lower() in output.lower()
