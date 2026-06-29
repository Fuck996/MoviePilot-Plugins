from pathlib import Path


def test_medialibrarykeeper_uses_official_emby_watch_state_queries() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert "IsPlayed=true" in source
    assert "Filters=IsPlayed" not in source
    assert "Filters=IsResumable" in source
    assert 'user_data.get("PlayCount")' not in source
    assert 'bool(cls._clean_text(user_data.get("LastPlayedDate")))' not in source
    assert "UserData.Played" in source
    assert "LastPlayedDate" in source
    assert "/Shows/{quote(item_id)}/Episodes" in source


def test_medialibrarykeeper_disk_discovery_keeps_mount_points_separate() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert '"key": mount_point' in source
    assert 'if str(parent) == current.anchor:' in source
    assert "unavailable" in source
    assert "_media_root_path" in source
