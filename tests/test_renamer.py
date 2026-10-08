from pathlib import Path

from music_shuffle.renamer import (
    RenameEntry,
    build_destination,
    build_unshuffle_plan,
    execute_plan,
    remove_prefix,
)


def test_remove_prefix():
    assert remove_prefix("000001 - Song.mp3") == "Song.mp3"
    assert remove_prefix("001 - Song.mp3", digits=3) == "Song.mp3"
    assert remove_prefix("Song.mp3") == "Song.mp3"


def test_remove_prefix_keeps_real_titles():
    assert remove_prefix("1979 - Smashing Pumpkins.mp3") == "1979 - Smashing Pumpkins.mp3"
    assert remove_prefix("123456-Song.mp3") == "123456-Song.mp3"


def test_remove_prefix_only_once():
    assert remove_prefix("000001 - 000002 - Song.mp3") == "000002 - Song.mp3"


def test_build_unshuffle_plan(tmp_path: Path):
    plan = build_unshuffle_plan(
        [tmp_path / "000001 - A.mp3", tmp_path / "B.mp3"]
    )
    assert [Path(e.new).name for e in plan] == ["A.mp3"]


def test_build_destination(tmp_path: Path):
    destination = build_destination(tmp_path / "Song.mp3", 42, 6)
    assert destination.name == "000042 - Song.mp3"


def test_execute_plan(tmp_path: Path):
    a = tmp_path / "001 - A.mp3"
    b = tmp_path / "002 - B.mp3"
    a.write_text("A")
    b.write_text("B")

    execute_plan([
        RenameEntry(str(a), str(tmp_path / "100 - A.mp3")),
        RenameEntry(str(b), str(tmp_path / "200 - B.mp3")),
    ])

    assert (tmp_path / "100 - A.mp3").read_text() == "A"
    assert (tmp_path / "200 - B.mp3").read_text() == "B"


def test_execute_plan_swap(tmp_path: Path):
    a = tmp_path / "a.mp3"
    b = tmp_path / "b.mp3"
    a.write_text("A")
    b.write_text("B")

    execute_plan([
        RenameEntry(str(a), str(b)),
        RenameEntry(str(b), str(a)),
    ])

    assert a.read_text() == "B"
    assert b.read_text() == "A"
