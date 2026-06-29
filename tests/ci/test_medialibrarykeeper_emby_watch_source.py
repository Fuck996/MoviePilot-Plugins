from pathlib import Path


def test_medialibrarykeeper_uses_official_emby_watch_state_queries() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert "IsPlayed=true" in source
    assert "Filters=IsPlayed" not in source
    assert "Filters=IsResumable" not in source
    assert 'user_data.get("PlayCount")' not in source
    assert 'bool(cls._clean_text(user_data.get("LastPlayedDate")))' not in source
    assert "UserData.Played" not in source
    assert "_is_played_user_data" not in source
    assert "started_episodes" not in source
    assert "watching" not in source
    assert "LastPlayedDate" in source
    assert "/Shows/{quote(item_id)}/Episodes" in source


def test_medialibrarykeeper_frontend_has_no_watching_filter() -> None:
    source = Path("plugins.v2/medialibrarykeeper/src/components/AppPage.vue").read_text(encoding="utf-8")

    assert "观看中" not in source
    assert "watching" not in source


def test_medialibrarykeeper_disk_discovery_keeps_mount_points_separate() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert '"key": mount_point' in source
    assert 'if str(parent) == current.anchor:' in source
    assert "unavailable" in source
    assert "_media_root_path" in source


def test_medialibrarykeeper_maps_emby_paths_to_moviepilot_paths() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert '"path_mappings": []' in source
    assert "_normalize_path_mappings" in source
    assert "_map_emby_path" in source
    assert "return sorted(normalized, key=lambda item: len(item[\"emby_path\"]), reverse=True)" in source
    assert 'paths = [self._map_emby_path(path) for path in emby_paths]' in source
    assert 'path = self._map_emby_path(episode.get("Path"))' in source
