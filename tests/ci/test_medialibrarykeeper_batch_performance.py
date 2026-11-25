"""Exercise production lookup methods without requiring a running MoviePilot."""
import ast
import logging
import threading
from functools import wraps
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple


def _load_methods():
    source = Path("plugins.v2/medialibrarykeeper/__init__.py")
    tree = ast.parse(source.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MediaLibraryKeeper")
    names = {
        "_clean_text", "_to_int", "_object_value", "_normalized_path_text",
        "_normalized_seed_task_name", "_downloader_torrent_summary",
        "_batch_downloaders", "_batch_torrent_index", "_related_downloader_torrents",
        "_enrich_download_tasks_from_configured_downloaders", "_expand_related_download_tasks",
        "_dedupe_download_tasks", "_batch_directory_children",
        "_query_download_history_by_path", "_batch_directory_mappings", "_fileitem_from_storage_path", "_media_file_paths",
    }
    cls.bases = []
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in cls.body} == names
    decorator = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_serialize_plan_mutation")
    ns = dict(globals(), logger=logging.getLogger("test"), StorageChain=Any, DownloaderHelper=lambda: object())
    exec(compile(ast.fix_missing_locations(ast.Module(body=[decorator, cls], type_ignores=[])), str(source), "exec"), ns)
    return ns["MediaLibraryKeeper"], ns["_serialize_plan_mutation"]


def test_1706_torrents_seven_items_one_fetch():
    cls, _ = _load_methods()
    p = cls()
    torrents = [{"hash": f"h{i}", "name": f"Movie {i}", "content_path": f"/movies/{i}"} for i in range(1706)]
    torrents[-1]["content_path"] = "/movies/0"
    calls = []
    module = SimpleNamespace(list_torrents=lambda **kw: calls.append(kw) or torrents)
    p._configured_seed_cleanup_downloaders = lambda helper: [("qb", SimpleNamespace(module=module, type="qbittorrent"))]
    p._find_downloader_torrent = lambda *a: (_ for _ in ()).throw(AssertionError("unnecessary targeted fetch"))
    lookup = {}
    for i in range(7):
        tasks = [{"download_hash": f"H{i}", "title": f"Movie {i}"}]
        merged = p._expand_related_download_tasks(p._enrich_download_tasks_from_configured_downloaders(tasks, lookup), lookup)
        assert merged[0]["task_name"] == f"Movie {i}"
        if i == 0:
            assert len(merged) == 2 and merged[1]["download_hash"] == "h1705"
        else:
            assert len(merged) == 1
    assert len(calls) == 1
    # A later batch must obtain a fresh snapshot, not stale deletion candidates.
    p._batch_torrent_index(module, "qb", {})
    assert len(calls) == 2


def test_directory_listing_is_scoped_to_storage_and_batch():
    cls, _ = _load_methods()
    p = cls()
    calls = []
    storage = SimpleNamespace(get_file_item=lambda **kw: kw, list_files=lambda item, **kw: calls.append(item) or [item])
    ctx = {}
    p._batch_directory_children(storage, "local", Path("/media/series"), ctx)
    p._batch_directory_children(storage, "local", Path("/media/series"), ctx)
    p._batch_directory_children(storage, "remote", Path("/media/series"), ctx)
    p._batch_directory_children(storage, "local", Path("/media/series"), {})
    assert len(calls) == 3


def test_plan_lock_rejects_duplicate_and_releases_after_exception():
    _, serialize = _load_methods()
    obj = SimpleNamespace(_plan_lock=threading.Lock())
    calls = []

    @serialize(lambda: "busy")
    def build(self, fail=False):
        calls.append(fail)
        assert build(self) == "busy"
        if fail:
            raise RuntimeError("failed")
        return "created"

    try:
        build(obj, True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected error")
    assert build(obj) == "created"
    assert calls == [True, False]


def test_series_history_parent_only_queried_and_contributed_once():
    cls, _ = _load_methods()
    p = cls()
    parent_calls = []
    exact_calls = []
    parent_rows = [SimpleNamespace(id=i) for i in range(100)]
    oper = SimpleNamespace(
        get_files_by_savepath=lambda **kw: parent_calls.append(kw) or parent_rows,
        get_file_by_fullpath=lambda **kw: exact_calls.append(kw) or None,
    )
    lookup = {}
    seen_parents = set()
    results = []
    for i in range(100):
        results.extend(p._query_download_history_by_path(oper, f"/series/e{i}.mkv", lookup, seen_parents))
    assert len(parent_calls) == 1 and len(exact_calls) == 100
    assert results == parent_rows
    # Another item in that directory gets the same records, with no stale cache
    # across batches and without re-querying within this batch.
    assert p._query_download_history_by_path(oper, "/series/e0.mkv", lookup, set()) == parent_rows
    assert len(parent_calls) == 1 and len(exact_calls) == 100
    p._query_download_history_by_path(oper, "/series/e0.mkv", {}, set())
    assert len(parent_calls) == 2


def test_directory_mappings_and_file_items_cached_per_batch():
    cls, _ = _load_methods()
    p = cls()
    calls = []
    p._directory_mappings = lambda: calls.append("config") or ["mapping"]
    lookup = {}
    assert p._batch_directory_mappings(lookup) == ["mapping"]
    assert p._batch_directory_mappings(lookup) == ["mapping"]
    assert calls == ["config"]
    storage = SimpleNamespace(get_file_item=lambda **kw: calls.append(kw) or {"size": 42})
    a = p._fileitem_from_storage_path(storage, "local", "/a.mkv", lookup)
    a["size"] = 0
    assert p._fileitem_from_storage_path(storage, "local", "/a.mkv", lookup)["size"] == 42
    p._fileitem_from_storage_path(storage, "remote", "/a.mkv", lookup)
    p._fileitem_from_storage_path(storage, "local", "/a.mkv", {})
    assert len(calls) == 4
