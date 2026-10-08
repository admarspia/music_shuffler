import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DIGITS = 6


@dataclass
class RenameEntry:
    old: str
    new: str


def remove_prefix(filename: str, digits: int = DEFAULT_DIGITS) -> str:
    """Remove a shuffle prefix written by this tool.

    Only ``<at least `digits` digits> - `` is stripped, so titles such as
    ``1979 - Smashing Pumpkins`` survive with the default width.
    """
    return re.sub(rf"^\d{{{digits},}} - ", "", filename, count=1)


def build_destination(source: Path, number: int, digits: int) -> Path:
    """Build the destination path for a source file."""
    original_name = remove_prefix(source.name, digits)
    return source.with_name(f"{number:0{digits}d} - {original_name}")


def build_plan(
    files: list[Path], numbers: list[int], digits: int
) -> list[RenameEntry]:
    """Create a list of source -> destination rename operations."""
    if len(files) != len(numbers):
        raise ValueError("Files and numbers must have the same length.")

    return [
        RenameEntry(
            old=str(source),
            new=str(build_destination(source, number, digits)),
        )
        for source, number in zip(files, numbers)
    ]


def build_unshuffle_plan(
    items: list[Path], digits: int = DEFAULT_DIGITS
) -> list[RenameEntry]:
    """Create rename operations that strip shuffle prefixes."""
    plan = []
    for source in items:
        stripped = remove_prefix(source.name, digits)
        if stripped and stripped != source.name:
            plan.append(
                RenameEntry(
                    old=str(source),
                    new=str(source.with_name(stripped)),
                )
            )
    return plan


def validate_destinations(plan: list[RenameEntry]) -> None:
    """Make sure the rename operation will not overwrite files."""
    sources = {Path(e.old).resolve() for e in plan}
    destinations = []

    for entry in plan:
        destination = Path(entry.new).resolve()
        if destination.exists() and destination not in sources:
            raise FileExistsError(f"Destination already exists: {destination}")
        destinations.append(destination)

    if len(destinations) != len(set(destinations)):
        raise ValueError("Multiple files would receive the same destination.")


def execute_plan(plan: list[RenameEntry]) -> None:
    """Execute a rename plan via temporary names, rolling back on failure."""
    if not plan:
        return

    validate_destinations(plan)

    temporary: list[tuple[Path, Path, Path]] = []

    try:
        # Phase 1: move everything to temporary names.
        for index, entry in enumerate(plan):
            source = Path(entry.old)
            counter = index
            temp = source.with_name(f".music_shuffle_tmp_{counter}_{source.name}")
            while temp.exists():
                counter += 1
                temp = source.with_name(
                    f".music_shuffle_tmp_{counter}_{source.name}"
                )
            source.rename(temp)
            temporary.append((temp, Path(entry.new), source))

        # Phase 2: move temporary files to their final names.
        for temp, destination, _ in temporary:
            temp.rename(destination)

    except Exception:
        # Best-effort rollback.
        for temp, destination, original in reversed(temporary):
            if destination.exists() and not temp.exists():
                destination.rename(temp)
            if temp.exists():
                temp.rename(original)
        raise


def save_history(history_file: Path, plan: list[RenameEntry]) -> None:
    """Save the rename operation for undo."""
    history_file.parent.mkdir(parents=True, exist_ok=True)
    data = [{"old": e.old, "new": e.new} for e in plan]
    with history_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def undo_history(history_file: Path) -> int:
    """Undo the most recent shuffle."""
    history_file = Path(history_file)

    if not history_file.exists():
        raise FileNotFoundError(f"No shuffle history found: {history_file}")

    with history_file.open(encoding="utf-8") as file:
        data = json.load(file)

    plan = [RenameEntry(item["old"], item["new"]) for item in data]

    # Validate everything first so a failure does not leave a partial undo.
    for entry in plan:
        if not Path(entry.new).exists():
            raise FileNotFoundError(f"Cannot undo; file is missing: {entry.new}")

    # The same two-phase approach as shuffling avoids collisions between
    # names that are both an old and a new path.
    reverse_plan = [RenameEntry(old=e.new, new=e.old) for e in plan]
    sources = {Path(e.old).resolve() for e in reverse_plan}
    for entry in reverse_plan:
        target = Path(entry.new).resolve()
        if target.exists() and target not in sources:
            raise FileExistsError(f"Cannot undo; path already exists: {target}")

    execute_plan(reverse_plan)
    history_file.unlink()
    return len(plan)
