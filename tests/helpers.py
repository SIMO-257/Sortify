def feed_inputs(monkeypatch, answers):
    """Make input() return the given answers in order."""
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda *_: next(answers))
