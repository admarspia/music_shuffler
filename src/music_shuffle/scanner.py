from pathlib import Path

DEFAULT_EXTENSIONS = {
    ".mp3", ".flac", ".ogg", ".wav", ".m4a",
    ".aac", ".opus", ".wma", ".alac", ".webm",
}


def normalize_extensions(extensions: set[str] | list[str] | None) -> set[str]:
    """Lower-case extensions and make sure they start with a dot."""
    return {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in (extensions or DEFAULT_EXTENSIONS)
    }


def _resolve_directory(directory: Path) -> Path:
    directory = Path(directory).expanduser().resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    return directory


def scan_directory(
    directory: Path,
    recursive: bool = False,
    extensions: set[str] | None = None,
) -> list[Path]:
    """Find supported music files in a directory."""
    directory = _resolve_directory(directory)
    exts = normalize_extensions(extensions)

    iterator = directory.rglob("*") if recursive else directory.iterdir()

    return sorted(
        (p for p in iterator if p.is_file() and p.suffix.lower() in exts),
        key=lambda p: str(p).lower(),
    )


def scan_albums(
    directory: Path,
    extensions: set[str] | None = None,
) -> list[Path]:
    """Find album folders: immediate, non-hidden subfolders containing music."""
    directory = _resolve_directory(directory)
    exts = normalize_extensions(extensions)

    albums = [
        child
        for child in directory.iterdir()
        if child.is_dir()
        and not child.name.startswith(".")
        and any(
            p.is_file() and p.suffix.lower() in exts for p in child.rglob("*")
        )
    ]

    return sorted(albums, key=lambda p: p.name.lower())
