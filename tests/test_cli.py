from pathlib import Path

from music_shuffle.cli import main


def test_shuffle_and_undo(tmp_path: Path):
    names = ["a.mp3", "b.mp3", "c.mp3"]
    for n in names:
        (tmp_path / n).write_text(n)

    assert main([str(tmp_path), "--seed", "1"]) == 0
    current = sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".mp3")
    assert all(" - " in n for n in current)

    assert main([str(tmp_path), "--undo"]) == 0
    assert sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".mp3") == names


def test_reshuffle_strips_old_prefix(tmp_path: Path):
    (tmp_path / "a.mp3").write_text("a")
    main([str(tmp_path), "--no-history"])
    main([str(tmp_path), "--no-history"])
    (name,) = [p.name for p in tmp_path.iterdir()]
    assert name.endswith(" - a.mp3") and name.count(" - ") == 1


def _music_names(path: Path):
    return sorted(p.name for p in path.iterdir() if not p.name.startswith("."))


def test_unshuffle_without_history(tmp_path: Path):
    for n in ["a.mp3", "b.mp3"]:
        (tmp_path / n).write_text(n)

    main([str(tmp_path), "--no-history"])
    assert main([str(tmp_path), "--unshuffle"]) == 0
    assert _music_names(tmp_path) == ["a.mp3", "b.mp3"]


def test_unshuffle_removes_stale_history(tmp_path: Path):
    (tmp_path / "a.mp3").write_text("a")
    main([str(tmp_path)])
    assert (tmp_path / ".music-shuffle-history.json").exists()
    main([str(tmp_path), "--unshuffle"])
    assert not (tmp_path / ".music-shuffle-history.json").exists()


def test_unshuffle_dry_run_changes_nothing(tmp_path: Path):
    (tmp_path / "a.mp3").write_text("a")
    main([str(tmp_path), "--no-history"])
    before = _music_names(tmp_path)
    assert main([str(tmp_path), "--unshuffle", "--dry-run"]) == 0
    assert _music_names(tmp_path) == before


def test_title_with_year_survives_reshuffle(tmp_path: Path):
    (tmp_path / "1979 - Smashing Pumpkins.mp3").write_text("x")
    main([str(tmp_path), "--no-history"])
    main([str(tmp_path), "--no-history"])
    (name,) = _music_names(tmp_path)
    assert name.endswith(" - 1979 - Smashing Pumpkins.mp3")


def test_album_shuffle_and_undo(tmp_path: Path):
    for album in ["Album A", "Album B", "Album C"]:
        (tmp_path / album).mkdir()
        (tmp_path / album / "01 - Track.mp3").write_text(album)

    assert main([str(tmp_path), "--group-by", "folder", "--seed", "3"]) == 0

    albums = _music_names(tmp_path)
    assert all(" - Album " in a for a in albums)
    for album in albums:
        assert (tmp_path / album / "01 - Track.mp3").exists()  # tracks untouched

    assert main([str(tmp_path), "--undo"]) == 0
    assert _music_names(tmp_path) == ["Album A", "Album B", "Album C"]


def test_album_unshuffle(tmp_path: Path):
    (tmp_path / "Album A").mkdir()
    (tmp_path / "Album A" / "t.mp3").write_text("t")
    main([str(tmp_path), "--group-by", "folder", "--no-history"])
    assert main([str(tmp_path), "--group-by", "folder", "--unshuffle"]) == 0
    assert _music_names(tmp_path) == ["Album A"]


def test_confirmation_declined(tmp_path: Path, monkeypatch):
    (tmp_path / "a.mp3").write_text("a")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert main([str(tmp_path), "--confirm-threshold", "0"]) == 1
    assert _music_names(tmp_path) == ["a.mp3"]


def test_confirmation_requires_yes_when_not_interactive(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / "a.mp3").write_text("a")
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert main([str(tmp_path), "--confirm-threshold", "0"]) == 1
    assert "--yes" in capsys.readouterr().err
    assert main([str(tmp_path), "--confirm-threshold", "0", "--yes"]) == 0
