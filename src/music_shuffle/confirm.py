import os
import sys
from typing import Callable

ENV_THRESHOLD = "MUSIC_SHUFFLE_CONFIRM_THRESHOLD"
DEFAULT_THRESHOLD = 25


class ConfirmationRequired(Exception):
    """Raised when confirmation is needed but no terminal is available."""


def default_threshold() -> int:
    """Read the confirmation threshold from the environment."""
    raw = os.environ.get(ENV_THRESHOLD)
    if raw is None:
        return DEFAULT_THRESHOLD
    try:
        return max(0, int(raw))
    except ValueError:
        return DEFAULT_THRESHOLD


def confirm_rename(
    count: int,
    location: str,
    threshold: int,
    assume_yes: bool = False,
    *,
    is_tty: bool | None = None,
    input_fn: Callable[[str], str] = input,
) -> bool:
    """Ask before renaming more than `threshold` items.

    Returns True when the operation may proceed. Raises ConfirmationRequired
    when a prompt is needed but stdin is not interactive.
    """
    if assume_yes or count <= threshold:
        return True

    if is_tty is None:
        is_tty = sys.stdin.isatty()

    if not is_tty:
        raise ConfirmationRequired(
            f"refusing to rename {count} items non-interactively; "
            "pass --yes to proceed"
        )

    answer = input_fn(
        f"About to rename {count} items in {location}. Continue? [y/N] "
    )
    return answer.strip().lower() in {"y", "yes"}
