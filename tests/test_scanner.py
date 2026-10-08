from pathlib import Path

from music_shuffle.scanner import scan_directory


def test_scan_non_recursive(tmp_path: Path):
    (tmp_path / "a.mp3").touch()
    (tmp_path / "b.txt").touch()
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.flac").touch()

    assert scan_directory(tmp_path) == [(tmp_path / "a.mp3").resolve()]


def test_scan_recursive(tmp_path: Path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.flac").touch()

    assert scan_directory(tmp_path, recursive=True) == [(sub / "c.flac").resolve()]


def test_scan_albums(tmp_path: Path):
    from music_shuffle.scanner import scan_albums

    (tmp_path / "Album A").mkdir()
    (tmp_path / "Album A" / "01.mp3").touch()
    (tmp_path / "Album B" / "CD1").mkdir(parents=True)
    (tmp_path / "Album B" / "CD1" / "01.flac").touch()
    (tmp_path / "Docs").mkdir()
    (tmp_path / "Docs" / "notes.txt").touch()
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / "x.mp3").touch()
    (tmp_path / "loose.mp3").touch()

    assert [p.name for p in scan_albums(tmp_path)] == ["Album A", "Album B"]
