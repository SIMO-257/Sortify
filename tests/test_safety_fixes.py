import os

import pytest

from Services import Service_4, Service_5, Service_6, Service_7, Service_10
from Tasks.group_files import group_by_extension
from Tasks.safety import blocked_reason, check_folder, clean_path, is_inside
from Tasks.ui import BackToMenu
from tests.helpers import feed_inputs


def make(tmp_path, *names):
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)


def test_empty_name_does_not_delete_anything(tmp_path, monkeypatch):
    make(tmp_path, "a.txt", "b.txt")
    for service in (Service_4, Service_5):
        feed_inputs(monkeypatch, [str(tmp_path), "", "b"])  # empty is re-asked, then back
        with pytest.raises(BackToMenu):
            service.run()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.txt", "b.txt"]


def test_delete_by_name_still_works(tmp_path, monkeypatch):
    make(tmp_path, "report1.txt", "keep.txt")
    feed_inputs(monkeypatch, [str(tmp_path), "report", "delete"])
    Service_4.run()
    assert [p.name for p in tmp_path.iterdir()] == ["keep.txt"]


def test_empty_folder_cleaner_never_removes_the_root(tmp_path, monkeypatch):
    root = tmp_path / "work"
    (root / "a" / "b").mkdir(parents=True)
    feed_inputs(monkeypatch, [str(root), "y"])
    Service_10.run()
    assert root.exists()
    assert list(root.iterdir()) == []


def test_empty_folder_cleaner_keeps_folders_with_files(tmp_path, monkeypatch):
    root = tmp_path / "work"
    (root / "full").mkdir(parents=True)
    (root / "full" / "f.txt").write_text("x")
    (root / "empty").mkdir()
    feed_inputs(monkeypatch, [str(root), "y"])
    Service_10.run()
    assert [p.name for p in root.iterdir()] == ["full"]


def test_move_never_overwrites(tmp_path, monkeypatch):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    make(src, "a.txt")
    make(dst, "a.txt")
    (dst / "a.txt").write_text("original")
    feed_inputs(monkeypatch, [str(src), "1", str(dst), "y"])
    Service_6.run()
    assert (dst / "a.txt").read_text() == "original"
    assert (dst / "a(1).txt").read_text() == "a.txt"


def test_recursive_move_keeps_same_named_files(tmp_path, monkeypatch):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    dst.mkdir()
    (src / "one").mkdir(parents=True)
    (src / "two").mkdir()
    (src / "one" / "a.txt").write_text("one")
    (src / "two" / "a.txt").write_text("two")
    feed_inputs(monkeypatch, [str(src), "1", str(dst), "y"])
    Service_7.run()
    assert sorted(p.read_text() for p in dst.iterdir()) == ["one", "two"]


def test_target_inside_source_is_refused(tmp_path, monkeypatch):
    src = tmp_path / "src"
    make(src, "a.txt")
    (src / "target").mkdir()
    feed_inputs(monkeypatch, [str(src), "1", str(src / "target"), "y"])
    Service_6.run()
    assert (src / "a.txt").exists()


def test_dangerous_folders_are_blocked():
    assert blocked_reason("/")
    assert blocked_reason(os.path.expanduser("~"))
    assert blocked_reason("/usr/lib")
    assert check_folder("/")[1]


def test_check_folder_cleans_quotes_and_rejects_files(tmp_path):
    folder = tmp_path / "f"
    folder.mkdir()
    assert check_folder(f'  "{folder}"  ') == (str(folder), None)
    (tmp_path / "file.txt").write_text("x")
    assert check_folder(str(tmp_path / "file.txt"))[1]
    assert check_folder(str(tmp_path / "missing"))[1]
    assert check_folder("")[1]


def test_clean_path_expands_home():
    assert clean_path("~") == os.path.expanduser("~")


def test_is_inside(tmp_path):
    assert is_inside(tmp_path / "a" / "b", tmp_path)
    assert is_inside(tmp_path, tmp_path)
    assert not is_inside(tmp_path, tmp_path / "a")


def test_trailing_dot_counts_as_no_extension():
    ext, none = group_by_extension([("/x/name.", "name.")])
    assert ext == {} and len(none) == 1
