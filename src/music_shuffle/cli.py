import argparse
import random
import sys
from pathlib import Path

from . import __version__
from .confirm import (
    ConfirmationRequired,
    confirm_rename,
    default_threshold,
)
from .renamer import (
    DEFAULT_DIGITS,
    build_plan,
    build_unshuffle_plan,
    execute_plan,
    save_history,
    undo_history,
)
from .scanner import normalize_extensions, scan_albums, scan_directory
from .shuffler import generate_unique_numbers


def parse_range(value: str) -> tuple[int, int]:
    """Parse MIN-MAX."""
    try:
        left, right = value.split("-", 1)
        minimum, maximum = int(left), int(right)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Range must look like MIN-MAX, for example 100000-999999."
        )

    if minimum < 0 or maximum < 0:
        raise argparse.ArgumentTypeError("Range values must be non-negative.")
    if minimum > maximum:
        raise argparse.ArgumentTypeError("MIN must not exceed MAX.")

    return minimum, maximum


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="music-shuffle",
        description=(
            "Randomly prefix music filenames (or album folders) with unique "
            "numbers while preserving their original titles."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("directory", nargs="?", type=Path)
    parser.add_argument(
        "--range", dest="number_range", type=parse_range,
        default=(100000, 999999), metavar="MIN-MAX",
        help="random number range (default: 100000-999999)",
    )
    parser.add_argument(
        "--digits", type=int, default=DEFAULT_DIGITS,
        help=f"minimum width of numeric prefix (default: {DEFAULT_DIGITS})",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="use a deterministic random seed",
    )
    parser.add_argument(
        "--group-by", choices=["none", "folder"], default="none",
        help=(
            "'folder' shuffles album folders instead of songs: folder names "
            "get the prefix and tracks inside are left untouched"
        ),
    )
    parser.add_argument(
        "--recursive", action="store_true",
        help="include music files in subdirectories (song mode only)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="show changes without renaming anything",
    )
    parser.add_argument(
        "--undo", action="store_true", help="undo the most recent shuffle"
    )
    parser.add_argument(
        "--unshuffle", action="store_true",
        help="remove shuffle prefixes (works without a history file)",
    )
    parser.add_argument(
        "--extensions", nargs="+", default=None,
        help="music extensions to include, for example mp3 flac ogg",
    )
    parser.add_argument(
        "--no-history", action="store_true", help="do not save undo history"
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="do not ask for confirmation",
    )
    parser.add_argument(
        "--confirm-threshold", type=int, default=default_threshold(),
        metavar="N",
        help=(
            "ask for confirmation when renaming more than N items "
            "(default: 25, env: MUSIC_SHUFFLE_CONFIRM_THRESHOLD; 0 = always)"
        ),
    )
    return parser


def _error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.directory is None:
        parser.error("a directory is required")
    if args.digits < 1:
        parser.error("--digits must be at least 1")
    if args.undo and args.unshuffle:
        parser.error("--undo and --unshuffle cannot be combined")

    directory = args.directory.expanduser().resolve()
    history_file = directory / ".music-shuffle-history.json"

    if args.undo:
        try:
            count = undo_history(history_file)
            print(f"Restored {count} items.")
            return 0
        except (FileNotFoundError, FileExistsError, OSError) as exc:
            return _error(str(exc))

    extensions = normalize_extensions(args.extensions)

    try:
        if args.group_by == "folder":
            items = scan_albums(directory, extensions)
            noun = "album folders"
        else:
            items = scan_directory(
                directory, recursive=args.recursive, extensions=extensions
            )
            noun = "music files"
    except NotADirectoryError as exc:
        return _error(str(exc))

    if not items:
        print(f"No {noun} found.")
        return 0

    try:
        if args.unshuffle:
            plan = build_unshuffle_plan(items, args.digits)
            if not plan:
                print("Nothing to unshuffle.")
                return 0
        else:
            minimum, maximum = args.number_range

            if args.digits > len(str(maximum)):
                return _error(
                    f"--digits={args.digits} is too wide "
                    f"for range {minimum}-{maximum}."
                )

            rng = random.Random(args.seed)
            shuffled = list(items)
            rng.shuffle(shuffled)

            numbers = generate_unique_numbers(
                len(shuffled), minimum, maximum, rng
            )
            numbers.sort()  # smaller numbers sort first alphabetically

            plan = build_plan(shuffled, numbers, args.digits)

        if args.dry_run:
            for entry in plan:
                print(Path(entry.old).name)
                print(f"  -> {Path(entry.new).name}")
            return 0

        try:
            proceed = confirm_rename(
                len(plan),
                str(directory),
                args.confirm_threshold,
                args.yes,
            )
        except ConfirmationRequired as exc:
            return _error(str(exc))

        if not proceed:
            print("Aborted.")
            return 1

        execute_plan(plan)

        if args.unshuffle:
            # Old history refers to names that no longer exist.
            history_file.unlink(missing_ok=True)
            print(f"Removed prefixes from {len(plan)} items.")
            return 0

        if not args.no_history:
            save_history(history_file, plan)

        print(f"Shuffled {len(plan)} {noun}.")
        if not args.no_history:
            print(f"Undo history: {history_file}")
        return 0

    except (ValueError, FileExistsError, OSError) as exc:
        return _error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
