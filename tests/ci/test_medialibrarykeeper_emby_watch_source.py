from pathlib import Path


def test_medialibrarykeeper_uses_user_data_for_emby_watch_state() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert "Filters=IsPlayed" not in source
    assert "IsPlayed=true" not in source
    assert "Filters=IsResumable" not in source
    assert "UserData.Played" in source
