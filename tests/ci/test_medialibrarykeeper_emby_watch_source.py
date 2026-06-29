from pathlib import Path


def test_medialibrarykeeper_uses_official_emby_watch_state_queries() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert "IsPlayed=true" in source
    assert "Filters=IsPlayed" not in source
    assert "Filters=IsResumable" not in source
    assert 'user_data.get("Played")' in source
    assert 'user_data.get("PlayCount")' not in source
    assert 'bool(cls._clean_text(user_data.get("LastPlayedDate")))' not in source
    assert "UserData.Played" in source
    assert "_fetch_emby_item_detail" in source
    assert "_needs_emby_user_data_detail" in source
    assert "_resolve_emby_scan_users" in source
    assert "_fetch_emby_user_data_by_item" in source
    assert "_merge_emby_user_data" in source
    assert "/Items/{quote(clean_id)}" in source
    assert "_resolve_emby_user_id" not in source
    assert "started_episodes" not in source
    assert "watching" not in source
    assert "LastPlayedDate" in source
    assert "/Shows/{quote(item_id)}/Episodes" in source


def test_medialibrarykeeper_frontend_has_no_watching_filter() -> None:
    source = Path("plugins.v2/medialibrarykeeper/src/components/AppPage.vue").read_text(encoding="utf-8")

    assert "观看中" not in source
    assert "watching" not in source
    assert "已播放" in source
    assert "summary.value.watched" in source


def test_medialibrarykeeper_frontend_media_cards_show_volume() -> None:
    source = Path("plugins.v2/medialibrarykeeper/src/components/AppPage.vue").read_text(encoding="utf-8")
    detail_rows_source = source.split("const selectedDetailInfoRows", 1)[1].split("function resolveImageUrl", 1)[0]

    assert "mediaVolumeText" in source
    assert "所在盘" in source
    assert "mdi-harddisk" in source
    assert "mlk-media-facts" in source
    assert "mlk-detail-aside-info" in source
    assert "selectedDetailInfoRows" in source
    assert "v-for=\"row in selectedDetailInfoRows\"" in source
    assert "selectedPlanExpanded" in source
    assert "selectedPlanHeaders" in source
    assert "待生成批次明细" in source
    assert ":loading=\"creatingPlan\"" in source
    assert ":loading=\"updatingPlan\"" in source
    assert "const planning = ref" not in source
    assert "filterCleanedMediaFromStatus" in source
    assert "cleanedMediaIdsFromHistory" in source
    assert "pending_plan:" in source
    assert "background: rgba(var(--v-theme-surface-variant), 0.42);" not in source
    assert "border-right: 1px solid rgba(var(--v-theme-primary), 0.16);" in source
    assert "linear-gradient(180deg, rgba(var(--v-theme-primary), 0.18)" in source
    assert "所属卷" not in detail_rows_source
    assert "卷剩余" not in detail_rows_source
    assert "最后一集添加" not in detail_rows_source


def test_medialibrarykeeper_does_not_register_api_on_plugin_reload() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")

    assert "register_plugin_api" not in source
    assert "PluginReload" not in source


def test_medialibrarykeeper_cleanup_uses_queue_and_keeps_details() -> None:
    source = Path("plugins.v2/medialibrarykeeper/__init__.py").read_text(encoding="utf-8")
    frontend = Path("plugins.v2/medialibrarykeeper/src/components/AppPage.vue").read_text(encoding="utf-8")
    provider = Path("plugins.v2/medialibrarykeeper/src/provider.js").read_text(encoding="utf-8")
    record_task_source = source.split("def _download_tasks_from_records", 1)[1].split("def _download_tasks_from_history", 1)[0]
    history_task_source = source.split("def _download_tasks_from_history", 1)[1].split("def _query_download_history_by_path", 1)[0]

    assert "DATA_KEY_CLEANUP_QUEUE" in source
    assert "_enqueue_cleanup_plan" in source
    assert "threading.Thread" in source
    assert "deleted_media_files" in source
    assert "deleted_scraping_files" in source
    assert "_with_scraping_targets" in source
    assert "DownloadHistoryOper" in source
    assert "get_file_by_fullpath" in source
    assert "_delete_seed_task_from_configured_downloaders" in source
    assert "_configured_seed_cleanup_downloaders" in source
    assert "_selected_downloader_names" not in record_task_source
    assert "_selected_downloader_names" not in history_task_source
    assert "SUPPORTED_DOWNLOADER_TYPES" not in record_task_source
    assert "SUPPORTED_DOWNLOADER_TYPES" not in history_task_source
    assert '"original_downloader": downloader' in source
    assert 'key = task.get("download_hash")' in source
    assert 'module.remove_torrents(' in source
    assert 'downloader=downloader' in source
    assert "媒体库管家保种任务删除开始" in source
    assert "媒体库管家保种任务删除尝试" in source
    assert "媒体库管家保种任务删除调用" in source
    assert "媒体库管家保种任务删除返回失败" in source
    assert "媒体库管家保种任务删除异常" in source
    assert "_prune_snapshot_after_cleanup" in source
    assert "_cleanup_removed_media_ids" in source
    assert "媒体库管家清理缓存刷新" in source
    assert "original_downloader" in frontend
    assert "original_downloader" in provider
    assert "status:v2" in provider
    assert "historyDetailDialog" in frontend
    assert "cleanupQueueRows" in frontend
    assert "compactQueueItem" in provider
    assert "deleted_targets" in provider


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
