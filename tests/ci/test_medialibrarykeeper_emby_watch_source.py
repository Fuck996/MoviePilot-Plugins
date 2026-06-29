from pathlib import Path


def test_medialibrarykeeper_uses_user_data_for_emby_watch_state() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert "Filters=IsPlayed" not in source
    assert "IsPlayed=true" not in source
    assert "Filters=IsResumable" not in source
    assert "UserData.Played" in source
    assert "PlayCount" in source
    assert "LastPlayedDate" in source
    assert "/Shows/{quote(item_id)}/Episodes" in source


def test_medialibrarykeeper_disk_discovery_keeps_mount_points_separate() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert '"key": mount_point' in source
    assert 'if str(parent) == current.anchor:' in source
    assert "unavailable" in source
    assert "_media_root_path" in source
