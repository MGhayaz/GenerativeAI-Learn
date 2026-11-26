from pathlib import Path

from models.schemas import PendingAction
from workflow.confirmation_message import build_confirmation_message, probe_target


def action(command: str) -> PendingAction:
    return PendingAction(tool_name="execute_command", arguments={"command": command})


def make_playground(tmp_path: Path) -> Path:
    playground = tmp_path / "playground"
    instagram = playground / "Instagram"

    (instagram / "sub").mkdir(parents=True, exist_ok=True)

    (instagram / "a.txt").write_text("hello", encoding="utf-8")
    (instagram / "b.txt").write_text("world", encoding="utf-8")

    return playground


def test_probe_counts_files_and_folders(tmp_path):
    info = probe_target(make_playground(tmp_path) / "Instagram")
    assert (info.kind, info.files, info.folders) == ("folder", 2, 1)
    assert info.size_bytes == 10


def test_probe_missing_and_file(tmp_path):
    playground = make_playground(tmp_path)
    assert probe_target(playground / "nope").kind == "missing"
    assert probe_target(playground / "Instagram" / "a.txt").kind == "file"


def test_probe_caps_large_folders(tmp_path):
    big = tmp_path / "big"
    big.mkdir()
    for i in range(30):
        (big / f"f{i}.txt").write_text("x")
    info = probe_target(big, limit=10)
    assert info.capped is True and info.files == 10


def test_delete_folder_message_has_impact(tmp_path):
    playground = make_playground(tmp_path)
    msg = build_confirmation_message(action('Remove-Item -Recurse -Force "Instagram"'), playground)
    assert "delete folder 'Instagram'" in msg.display
    assert "2 files" in msg.display and "1 folder" in msg.display
    assert "everything inside" in msg.display
    assert "cannot be undone" in msg.display
    assert "Remove-Item" in msg.display          # poori command display mein
    assert "Remove-Item" not in msg.spoken        # spoken mein code nahi
    assert "3 items" in msg.spoken
    assert "in playground" in msg.spoken


def test_real_world_compound_command(tmp_path):
    playground = make_playground(tmp_path)
    command = (
        f'cd {playground.as_posix()}; if (Test-Path "Instagram") '
        '{ Remove-Item -Recurse -Force "Instagram"; "Deleted" } else { "missing" }'
    )
    msg = build_confirmation_message(action(command), playground)
    assert "delete folder 'Instagram'" in msg.display
    assert "2 files" in msg.display


def test_empty_folder(tmp_path):
    msg = build_confirmation_message(action("Remove-Item empty_dir"), make_playground(tmp_path))
    assert "empty" in msg.display
    assert "everything inside" not in msg.display


def test_missing_target_says_nothing_will_change(tmp_path):
    msg = build_confirmation_message(action('Remove-Item "ghost"'), make_playground(tmp_path))
    assert "not found" in msg.display


def test_outside_playground_is_flagged(tmp_path):
    playground = make_playground(tmp_path)
    outside = tmp_path / "other"
    outside.mkdir()
    msg = build_confirmation_message(action(f'Remove-Item "{outside.as_posix()}"'), playground)
    assert "OUTSIDE" in msg.display
    assert "not your playground" in msg.spoken


def test_traversal_path_is_flagged_as_outside(tmp_path):
    playground = make_playground(tmp_path)
    msg = build_confirmation_message(action('Remove-Item "..\\other"'), playground)
    assert "OUTSIDE" in msg.display


def test_wildcard_skips_probe(tmp_path):
    msg = build_confirmation_message(action('Remove-Item "*.txt"'), make_playground(tmp_path))
    assert "matching" in msg.spoken


def test_unparseable_command_gets_generic_message(tmp_path):
    for command in ("git reset --hard HEAD", "", "Remove-Item"):
        msg = build_confirmation_message(action(command), make_playground(tmp_path))
        assert "can change your files" in msg.spoken
        assert "Say yes" in msg.display


def test_spoken_has_no_code_symbols(tmp_path):
    msg = build_confirmation_message(action('Remove-Item -Recurse "Instagram"'), make_playground(tmp_path))
    for symbol in ("\\", "`", "{", "}", ";", "Remove-Item"):
        assert symbol not in msg.spoken