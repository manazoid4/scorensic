"""Deliberately faulty: raw string equality. "42.0", "canberra" or a trailing newline fail."""


def grade(task, output):
    return output == task["reference"]
