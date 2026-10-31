"""Deliberately faulty: a module-level counter flips every fifth verdict (hidden shared state)."""
_calls = 0


def grade(task, output):
    global _calls
    _calls += 1
    correct = " ".join(output.split()).lower() == task["reference"].lower()
    return (not correct) if _calls % 5 == 0 else correct
