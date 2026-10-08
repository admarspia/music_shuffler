import pytest

from music_shuffle.confirm import (
    ConfirmationRequired,
    confirm_rename,
    default_threshold,
)


def test_below_threshold_needs_no_prompt():
    assert confirm_rename(5, "x", 25, is_tty=False) is True


def test_assume_yes_skips_prompt():
    assert confirm_rename(500, "x", 25, assume_yes=True, is_tty=False) is True


def test_non_interactive_requires_yes():
    with pytest.raises(ConfirmationRequired):
        confirm_rename(500, "x", 25, is_tty=False)


@pytest.mark.parametrize("answer,expected", [("y", True), ("YES", True), ("", False), ("n", False)])
def test_prompt_answers(answer, expected):
    assert confirm_rename(500, "x", 25, is_tty=True, input_fn=lambda _: answer) is expected


def test_threshold_from_env(monkeypatch):
    monkeypatch.setenv("MUSIC_SHUFFLE_CONFIRM_THRESHOLD", "3")
    assert default_threshold() == 3
    monkeypatch.setenv("MUSIC_SHUFFLE_CONFIRM_THRESHOLD", "oops")
    assert default_threshold() == 25
