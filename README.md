# Music Shuffle

A small command-line utility that creates a persistent shuffle order for music
players by adding unique random numeric prefixes to filenames, or to album
folder names.

    Pink Floyd - Time.mp3   ->   381729 - Pink Floyd - Time.mp3
    Radiohead - Creep.mp3   ->   047182 - Radiohead - Creep.mp3
    Nirvana - Lithium.mp3   ->   829451 - Nirvana - Lithium.mp3

The original title stays visible. Run it again for a new random order.

## Why?

Some players only sort by name. A random numeric prefix makes the ordinary
sort order a shuffled playback order.

## Features

- Unique random numeric prefixes; original titles preserved
- **Album shuffle**: shuffle whole albums, keep track order inside them
- **Unshuffle**: remove prefixes at any time, no history file required
- **Confirmation prompt** for large renames, with `--yes` for scripts
- Re-shuffle on every run (old prefixes are replaced, not stacked)
- Dry-run preview, undo, optional deterministic seed
- Configurable number range, prefix width and extensions
- Collision-safe two-phase renames with rollback on failure
- No runtime dependencies

## Requirements

Python 3.10+

## Installation

    git clone https://github.com/YOUR_USERNAME/music-shuffle.git
    cd music-shuffle
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .

## Quick start

    music-shuffle ~/Music --dry-run       # preview
    music-shuffle ~/Music                 # shuffle songs
    music-shuffle ~/Music --undo          # restore previous names
    music-shuffle ~/Music --unshuffle     # strip prefixes entirely

## Shuffling songs

    music-shuffle ~/Music
    music-shuffle ~/Music --recursive     # include subdirectories
    music-shuffle ~/Music --seed 12345    # reproducible
    music-shuffle ~/Music --range 10000000-99999999 --digits 8
    music-shuffle ~/Music --extensions mp3 flac opus

Default range is `100000-999999` (inclusive). Default extensions:
`.mp3 .flac .ogg .wav .m4a .aac .opus .wma .alac`.

## Album shuffle

    music-shuffle ~/Music --group-by folder

Given:

    ~/Music/
    ├── Abbey Road/        01 - Come Together.mp3 ...
    ├── Kind of Blue/      01 - So What.flac ...
    └── OK Computer/       01 - Airbag.mp3 ...

you get:

    ~/Music/
    ├── 214803 - OK Computer/
    ├── 536218 - Abbey Road/
    └── 902771 - Kind of Blue/

Track files inside each album are **not touched**, so albums play in their
original track order while the album order is shuffled.

Notes:

- An *album* is an immediate, non-hidden subfolder of the target directory
  that contains at least one music file (at any depth, so `CD1/CD2` layouts
  work).
- Loose music files directly in the target directory are ignored in this mode.
- `--recursive` has no effect in this mode.
- `--undo`, `--unshuffle`, `--dry-run`, `--seed`, `--range` and `--digits`
  all work the same way.

Why folders? A player sorts by folder first and file name second, so file
prefixes alone cannot reorder tracks across different folders.

## Unshuffle

    music-shuffle ~/Music --unshuffle
    music-shuffle ~/Music --group-by folder --unshuffle
    music-shuffle ~/Music --unshuffle --dry-run

Removes the prefixes written by this tool. Use it when the undo history is
missing or you renamed files by hand since the last shuffle.

- Only names that match `<at least --digits digits> - ` are changed. If you
  shuffled with a custom width, pass the same `--digits` value.
  Titles such as `1979 - Smashing Pumpkins.mp3` are left alone under the
  default width of 6.
- If stripping would make two names identical, nothing is renamed and an
  error is reported.
- Any existing undo history is deleted afterwards because it no longer
  describes the folder.

## Confirmation prompt

When a run would rename more than N items, you are asked first:

    About to rename 312 items in /home/me/Music. Continue? [y/N]

| Option / variable | Effect |
| --- | --- |
| `--confirm-threshold N` | Prompt when renaming more than `N` items (default `25`; `0` = always) |
| `MUSIC_SHUFFLE_CONFIRM_THRESHOLD` | Same, set via environment; the flag wins |
| `-y`, `--yes` | Never prompt |

Without a terminal (cron, pipes) a run above the threshold fails with an
error instead of hanging; pass `--yes` for unattended use. `--dry-run` never
prompts and never changes anything.

## Undo

A normal shuffle writes `.music-shuffle-history.json` in the target directory.
`--undo` restores the previous names and removes the file. Undo checks
everything first and renames collision-safely, so it does not leave a
half-restored library. Use `--no-history` to skip writing history.

Undo only reverses the most recent shuffle. To clean up older ones, use
`--unshuffle`.

## All options

| Option | Description |
| --- | --- |
| `directory` | Folder to process (required) |
| `--group-by {none,folder}` | Shuffle songs (default) or album folders |
| `--recursive` | Include subdirectories (song mode) |
| `--range MIN-MAX` | Prefix number range, default `100000-999999` |
| `--digits N` | Minimum prefix width, default `6` |
| `--seed N` | Deterministic shuffle |
| `--extensions EXT...` | Extensions to include |
| `--dry-run` | Preview only |
| `--undo` | Restore names from the last shuffle |
| `--unshuffle` | Remove prefixes |
| `--no-history` | Do not write undo history |
| `-y`, `--yes` | Skip confirmation |
| `--confirm-threshold N` | Confirmation threshold |
| `--version` | Show version |

`--undo` and `--unshuffle` cannot be combined.

## How it works

1. Items (files or album folders) are scanned and randomly permuted.
2. Unique random numbers are drawn from the range and sorted ascending.
3. The i-th shuffled item gets the i-th number as a prefix.
4. A normal name sort now yields the shuffled order.

Renames go through temporary names first (`A -> tmp-A`, then `tmp-A -> B`),
so swapping or reusing names cannot collide or overwrite anything. If a step
fails, completed renames are rolled back on a best-effort basis.

## Safety

Only names change, never audio data. Try `--dry-run` first and keep a backup
of collections you care about. Prefer testing on a copy.

## Project structure

    music-shuffle/
    ├── src/music_shuffle/
    │   ├── cli.py        # argument parsing and orchestration
    │   ├── scanner.py    # find songs / album folders
    │   ├── shuffler.py   # unique random numbers
    │   ├── renamer.py    # plans, safe execution, history, undo
    │   └── confirm.py    # confirmation prompt logic
    ├── tests/
    ├── CHANGELOG.md
    └── pyproject.toml

## Development

    pip install -e . pytest
    pytest

## Roadmap

- Multiple shuffle histories
- Tag-aware album grouping and filtering (optional `mutagen`)
- Ignore patterns, config file
- Playlist export, shell completion
- Filename length checks for FAT32/exFAT devices

## License

MIT
