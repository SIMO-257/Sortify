import os

import pytest

import index
from Services import Service_0, Service_1, Service_2, Service_3, Service_8, Service_9
from Tasks.ui import BackToMenu, QuitProgram
from tests.helpers import feed_inputs


def names(path):
    return sorted(p.name for p in path.iterdir())


def test_menu_is_sorted_numerically():
    order = [s["name"] for s in index.load_services()]
    assert order[0].startswith("File Organizer Extension Based - [flat]")
    assert order[-1] == "Empty Directories Cleaner"
    assert len(order) == 11


def test_organize_flat_ignores_subfolders(tmp_path, monkeypatch):
    (tmp_path / "a.pdf").write_text("x")
    (tmp_path / "b.PDF").write_text("x")
    (tmp_path / "noext").write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.pdf").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "Office Docs!", "y"])
    Service_0.run()
    assert names(tmp_path) == ["office_docs_no_extension", "office_docs_pdf", "sub"]
    assert names(tmp_path / "office_docs_pdf") == ["a.pdf", "b.PDF"]
    assert names(tmp_path / "sub") == ["c.pdf"]


def test_organize_recursive_picks_up_subfolders(tmp_path, monkeypatch):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.txt").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "x", "y"])
    Service_1.run()
    assert names(tmp_path / "x_txt") == ["c.txt"]


def test_cancel_changes_nothing(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "x", "n"])
    Service_0.run()
    assert names(tmp_path) == ["a.txt"]


def test_folder_prompt_reasks_until_valid(tmp_path, monkeypatch, capsys):
    (tmp_path / "a.txt").write_text("x")
    feed_inputs(monkeypatch, ["/definitely/not/here", "/", str(tmp_path), "x", "n"])
    Service_0.run()
    out = capsys.readouterr().out
    assert "does not exist" in out and "Refusing" in out


def test_delete_by_extension_needs_the_word_delete(tmp_path, monkeypatch):
    (tmp_path / "a.tmp").write_text("x")
    (tmp_path / "b.txt").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "1", "yes", "delete"])
    Service_2.run()
    assert names(tmp_path) == ["b.txt"]


def test_delete_preview_is_capped(tmp_path, monkeypatch, capsys):
    for i in range(30):
        (tmp_path / f"f{i}.tmp").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "1", "n"])
    Service_3.run()
    assert "...and 10 more" in capsys.readouterr().out
    assert len(list(tmp_path.iterdir())) == 30


def test_recursive_delete_prints_one_summary(tmp_path, monkeypatch, capsys):
    for i in range(3):
        (tmp_path / f"f{i}.tmp").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "1", "delete"])
    Service_3.run()
    out = capsys.readouterr().out
    assert out.count("DELETION COMPLETE") == 1
    assert "Deleted: 3" in out


def test_date_organizer_groups_by_day(tmp_path, monkeypatch):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("x"); b.write_text("x")
    os.utime(a, (86400 * 365, 86400 * 365))
    os.utime(b, (86400 * 400, 86400 * 400))
    feed_inputs(monkeypatch, [str(tmp_path), "y"])
    Service_8.run()
    assert len(names(tmp_path)) == 2
    feed_inputs(monkeypatch, [str(tmp_path), "n"])
    Service_9.run()


def test_failures_are_reported(tmp_path, monkeypatch, capsys):
    (tmp_path / "a.tmp").write_text("x")
    feed_inputs(monkeypatch, [str(tmp_path), "1", "delete"])
    monkeypatch.setattr(os, "remove", lambda p: (_ for _ in ()).throw(PermissionError("denied")))
    Service_2.run()
    out = capsys.readouterr().out
    assert "Failed:  1" in out and "denied" in out


def test_back_returns_to_menu(monkeypatch):
    feed_inputs(monkeypatch, ["1", "b", "q"])
    index.main()


def test_quit_inside_service(monkeypatch, capsys):
    feed_inputs(monkeypatch, ["1", "q"])
    index.main()
    assert "Goodbye!" in capsys.readouterr().out


def test_back_and_quit_exceptions(tmp_path, monkeypatch):
    feed_inputs(monkeypatch, ["b"])
    with pytest.raises(BackToMenu):
        Service_0.run()
    feed_inputs(monkeypatch, ["q"])
    with pytest.raises(QuitProgram):
        Service_0.run()
