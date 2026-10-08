# Changelog

## 0.2.0

### Added
- `--group-by folder`: shuffle album folders instead of songs. Folder names
  get the prefix; tracks inside each album are left untouched.
- `--unshuffle`: strip shuffle prefixes without needing the history file.
  Supports `--dry-run` and `--group-by folder`, and removes stale history.
- Confirmation prompt before renaming more than N items
  (`--confirm-threshold N`, env `MUSIC_SHUFFLE_CONFIRM_THRESHOLD`, default 25).
  `-y/--yes` skips it; non-interactive runs refuse to proceed without `--yes`.
- `python -m music_shuffle` entry point.

### Changed
- Prefix stripping is now strict: only `<at least --digits digits> - ` is
  removed. Titles like `1979 - Smashing Pumpkins.mp3` are no longer damaged
  on re-shuffle. Prefixes written by 0.1.0 with the default width still match.
- `--undo` is now all-or-nothing and collision-safe; it validates first and
  uses the same two-phase rename as shuffling.
- Failures while moving files to temporary names are now rolled back too.

## 0.1.0
- Initial release: unique random prefixes, dry-run, undo, seed, recursive
  scan, configurable extensions, collision-safe renames.
