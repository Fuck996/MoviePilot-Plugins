import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from apscheduler.triggers.cron import CronTrigger
from fastapi import Body

from app import schemas
from app.api.endpoints.plugin import register_plugin_api
from app.chain.storage import StorageChain
from app.core.config import settings
from app.core.event import Event, eventmanager
from app.db.transferhistory_oper import TransferHistoryOper
from app.helper.mediaserver import MediaServerHelper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import NotificationType
from app.schemas.types import EventType

try:
    from app.db.models.transferhistory import TransferHistory
except Exception:
    TransferHistory = None


class MediaLibraryKeeper(_PluginBase):
    """
    媒体库管家。
    通过 MoviePilot 已配置的媒体服务器读取 Emby 媒体库，并复用整理记录与 StorageChain 执行清理。
    """

    plugin_name = "媒体库管家"
    plugin_desc = "管理 Emby 媒体库观看进度、空间风险和清理计划。"
    plugin_icon = "emby.png"
    plugin_version = "0.3.3"
    plugin_author = "fuck996"
    author_url = "https://github.com/Fuck996"
    plugin_config_prefix = "medialibrarykeeper_"
    plugin_order = 48
    auth_level = 1

    DATA_KEY_HISTORY = "history"
    DATA_KEY_PENDING_PLAN = "pending_plan"
    DATA_KEY_SNAPSHOT = "snapshot"
    DATA_KEY_LAST_DISK_WARNING = "last_disk_warning"

    def __init__(self):
        super().__init__()
        self._config: Dict[str, Any] = self._default_config()
        self._enabled = False

    def init_plugin(self, config: dict = None):
        config = self._normalize_config(config or {})
        self._config = config
        self._enabled = bool(config.get("enabled"))

    def get_state(self) -> bool:
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_service(self) -> Optional[List[Dict[str, Any]]]:
        if not self._enabled or not self._config.get("scan_cron"):
            return None
        try:
            trigger = CronTrigger.from_crontab(self._config["scan_cron"])
        except Exception as err:
            logger.error(f"媒体库管家定时扫描 Cron 配置无效：{err}")
            return None
        return [
            {
                "id": "MediaLibraryKeeperScan",
                "name": "媒体库管家定时扫描",
                "trigger": trigger,
                "func": self.scan_library,
                "kwargs": {"notify_disk_warning": True},
            }
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/status",
                "endpoint": self.get_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取媒体库管家状态",
            },
            {
                "path": "/config",
                "endpoint": self.save_config_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "保存媒体库管家配置",
            },
            {
                "path": "/scan",
                "endpoint": self.scan_library_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "拉取媒体库数据",
            },
            {
                "path": "/cleanup/plan",
                "endpoint": self.create_cleanup_plan_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "生成清理计划",
            },
            {
                "path": "/cleanup/execute",
                "endpoint": self.execute_cleanup_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "执行清理计划",
            },
            {
                "path": "/history",
                "endpoint": self.get_history_api,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取清理执行记录",
            },
        ]

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        return "vue", "dist/assets"

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [], self._config

    def get_page(self) -> List[dict]:
        return []

    def get_sidebar_nav(self) -> List[Dict[str, Any]]:
        if not self.get_state() or not self._config.get("show_sidebar_nav", True):
            return []
        return [
            {
                "nav_key": "main",
                "title": "媒体库管家",
                "icon": "mdi-database-search-outline",
                "section": "organize",
                "permission": "manage",
                "order": 48,
            }
        ]

    def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
        if not self.get_state():
            return None
        return [{"key": "summary", "name": "媒体库管家"}]

    def get_dashboard(self, key: str, **kwargs):
        if not self.get_state():
            return None
        summary = self._build_summary()
        subtitle = f"电影 {summary['movies']} / 剧集 {summary['series']} / 可释放 {self._human_size(summary['estimated_reclaim_size'])}"
        return (
            {"cols": 12, "sm": 6, "md": 4},
            {
                "title": "媒体库管家",
                "subtitle": subtitle,
                "refresh": 60,
                "border": True,
            },
            None,
        )

    def stop_service(self):
        pass

    def get_status(self) -> schemas.Response:
        snapshot = self._load_snapshot()
        return schemas.Response(
            success=True,
            data={
                "config": self._config,
                "summary": self._build_summary(snapshot),
                "libraries": snapshot.get("libraries", []),
                "media": snapshot.get("media", []),
                "recommendations": self._build_recommendations(snapshot),
                "pending_plan": self.get_data(self.DATA_KEY_PENDING_PLAN) or None,
                "history": self._load_history(),
                "capabilities": self._capabilities(),
                "media_server_options": self._media_server_options(),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    def save_config_api(self, config: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        try:
            self._config = self._normalize_config(config or {})
            self._enabled = bool(self._config.get("enabled"))
            self.update_config(self._config)
            return schemas.Response(success=True, data=self.get_status().data)
        except Exception as err:
            logger.error(f"保存媒体库管家配置失败：{err}")
            return schemas.Response(success=False, message=str(err))

    def scan_library_api(self) -> schemas.Response:
        try:
            self.scan_library(notify_disk_warning=True)
            return schemas.Response(success=True, message="媒体库扫描完成", data=self.get_status().data)
        except Exception as err:
            logger.error(f"媒体库管家扫描失败：{err}")
            return schemas.Response(success=False, message=str(err), data=self.get_status().data)

    def scan_library(self, notify_disk_warning: bool = False) -> Dict[str, Any]:
        services = self._active_emby_services()
        if not services:
            raise RuntimeError("没有可用的 Emby 媒体服务器，请先在 MoviePilot 媒体服务器中完成配置。")

        libraries: List[Dict[str, Any]] = []
        media: List[Dict[str, Any]] = []
        errors: List[str] = []
        for server_name, service_info in services.items():
            service = service_info.instance
            try:
                users = self._fetch_emby_users(service)
                if not users:
                    errors.append(f"{server_name} 未返回用户信息")
                    continue
                user_id = users[0].get("Id")
                server_libraries = self._fetch_emby_libraries(service, service_info, server_name, user_id)
                libraries.extend(server_libraries)
                library_index = {item["item_id"]: item for item in server_libraries if item.get("item_id")}
                media.extend(self._fetch_emby_items(service, service_info, server_name, user_id, library_index))
            except Exception as err:
                logger.error(f"媒体库管家读取 Emby {server_name} 失败：{err}")
                errors.append(f"{server_name}: {err}")

        snapshot = {
            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "libraries": self._dedupe_libraries(libraries),
            "media": self._dedupe_media(media),
            "errors": errors,
        }
        self.save_data(self.DATA_KEY_SNAPSHOT, snapshot)

        if notify_disk_warning:
            self._notify_disk_warning(snapshot)
        return snapshot

    def create_cleanup_plan_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        selected_ids = [self._clean_text(item) for item in payload.get("item_ids") or [] if self._clean_text(item)]
        selected_items = payload.get("items") or []
        if not selected_ids and selected_items:
            selected_ids = [self._clean_text(item.get("id")) for item in selected_items if self._clean_text(item.get("id"))]
        if not selected_ids:
            return schemas.Response(success=False, message="请先选择要清理的媒体条目")

        snapshot = self._load_snapshot()
        media_index = {item.get("id"): item for item in snapshot.get("media", [])}
        missing = [item_id for item_id in selected_ids if item_id not in media_index]
        if missing:
            return schemas.Response(success=False, message="所选媒体不在最近一次扫描结果中，请先重新扫描媒体库。")

        delete_source = bool(payload.get("delete_source", self._config.get("default_delete_source")))
        plan_items = [self._build_plan_item(media_index[item_id], delete_source) for item_id in selected_ids]
        ready_count = len([item for item in plan_items if item.get("status") == "ready"])
        estimated_size = self._sum_unique_target_size(plan_items)
        plan_status = "ready" if ready_count == len(plan_items) else "blocked"
        plan = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "delete_source": delete_source,
            "items": plan_items,
            "estimated_reclaim_size": estimated_size,
            "ready_count": ready_count,
            "status": plan_status,
            "message": self._plan_message(plan_status, plan_items),
        }
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        return schemas.Response(success=True, data={"plan": plan, "status": self.get_status().data})

    def execute_cleanup_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        plan_id = self._clean_text(payload.get("plan_id"))
        confirm = bool(payload.get("confirm"))
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        if not plan_id or pending_plan.get("id") != plan_id:
            return schemas.Response(success=False, message="清理计划不存在或已失效")
        if not confirm:
            return schemas.Response(success=False, message="执行清理前需要在页面确认删除范围。")
        if pending_plan.get("status") != "ready":
            return schemas.Response(success=False, message=pending_plan.get("message") or "清理计划尚未就绪，不能执行删除。")

        result = self._execute_plan(pending_plan)
        history = self._load_history()
        history.insert(0, result)
        self.save_data(self.DATA_KEY_HISTORY, history[:50])
        if result["status"] == "success":
            self.save_data(self.DATA_KEY_PENDING_PLAN, None)
        if self._config.get("notify_enabled"):
            self._notify_cleanup_result(result)
        return schemas.Response(success=result["status"] == "success", message=result["message"], data=self.get_status().data)

    def get_history_api(self) -> schemas.Response:
        return schemas.Response(success=True, data={"history": self._load_history()})

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        return {
            "enabled": False,
            "show_sidebar_nav": True,
            "notify_enabled": True,
            "disk_warning_enabled": True,
            "disk_warning_free_gb": 200,
            "disk_warning_free_percent": 10,
            "scan_cron": "0 */6 * * *",
            "ai_suggestions": False,
            "default_delete_source": False,
            "mediaservers": [],
            "library_names": [],
        }

    @classmethod
    def _normalize_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        defaults = cls._default_config()
        normalized = {**defaults, **(config or {})}
        for key in ["enabled", "show_sidebar_nav", "notify_enabled", "disk_warning_enabled", "ai_suggestions", "default_delete_source"]:
            normalized[key] = bool(normalized.get(key, defaults[key]))
        normalized["disk_warning_free_gb"] = max(cls._to_int(normalized.get("disk_warning_free_gb"), 200), 0)
        normalized["disk_warning_free_percent"] = max(cls._to_int(normalized.get("disk_warning_free_percent"), 10), 0)
        normalized["scan_cron"] = cls._clean_text(normalized.get("scan_cron")) or defaults["scan_cron"]
        for key in ["mediaservers", "library_names"]:
            normalized[key] = cls._to_list(normalized.get(key))
        return normalized

    @staticmethod
    def _to_list(value: Any) -> List[str]:
        if isinstance(value, str):
            return [line.strip() for line in value.splitlines() if line.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item or "").strip()]
        return []

    @staticmethod
    def _to_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clean_text(value: Any) -> str:
        return str(value or "").strip()

    def _media_server_options(self) -> List[Dict[str, str]]:
        options = []
        try:
            for config in MediaServerHelper().get_configs().values():
                name = self._clean_text(getattr(config, "name", ""))
                if name:
                    options.append({"title": name, "value": name})
        except Exception as err:
            logger.warning(f"媒体库管家读取媒体服务器配置失败：{err}")
        return options

    def _active_emby_services(self) -> Dict[str, Any]:
        name_filters = self._config.get("mediaservers") or None
        services = MediaServerHelper().get_services(type_filter="emby", name_filters=name_filters) or {}
        active_services = {}
        for name, service_info in services.items():
            instance = getattr(service_info, "instance", None)
            if not instance:
                continue
            if hasattr(instance, "is_inactive") and instance.is_inactive():
                logger.warning(f"媒体服务器 {name} 未连接，已跳过")
                continue
            active_services[name] = service_info
        return active_services

    def _fetch_emby_users(self, service: Any) -> List[Dict[str, Any]]:
        response = service.get_data("[HOST]Users?&api_key=[APIKEY]")
        data = response.json() if hasattr(response, "json") else response
        return data if isinstance(data, list) else []

    def _fetch_emby_libraries(self, service: Any, service_info: Any, server_name: str, user_id: str) -> List[Dict[str, Any]]:
        response = service.get_data(f"[HOST]emby/Users/{user_id}/Views?api_key=[APIKEY]")
        data = response.json() if hasattr(response, "json") else response
        raw_items = data.get("Items") if isinstance(data, dict) else []
        libraries = []
        for item in raw_items:
            library = self._normalize_emby_library(item, service_info, server_name)
            if library and self._accept_library_name(library.get("title")):
                libraries.append(library)
        return libraries

    def _fetch_emby_items(
        self,
        service: Any,
        service_info: Any,
        server_name: str,
        user_id: str,
        library_index: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        start = 0
        limit = 200
        fields = quote(
            "DateCreated,Path,Genres,ProviderIds,Overview,PrimaryImageAspectRatio,BasicSyncInfo,UserData,"
            "ChildCount,RecursiveItemCount,ProductionYear,CommunityRating,CriticRating,SortName,MediaSources,"
            "ParentId,PremiereDate,RunTimeTicks,ImageTags,BackdropImageTags"
        )
        while True:
            url = (
                f"[HOST]emby/Users/{user_id}/Items?Recursive=true&IncludeItemTypes=Movie,Series"
                f"&Fields={fields}&ImageTypeLimit=1&EnableTotalRecordCount=false"
                f"&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            for item in raw_items:
                normalized = self._normalize_emby_item(item, service_info, server_name, library_index)
                if not normalized:
                    continue
                if normalized.get("type") == "series":
                    stats = self._fetch_series_episode_stats(service, user_id, normalized.get("item_id"))
                    if stats:
                        normalized["total_episodes"] = stats["total_episodes"] or normalized.get("total_episodes", 0)
                        normalized["watched_episodes"] = stats["watched_episodes"]
                        normalized["size"] = stats["size"] or normalized.get("size", 0)
                        normalized["episode_paths"] = stats["paths"]
                        normalized["watched"] = (
                            normalized["total_episodes"] > 0
                            and normalized["watched_episodes"] >= normalized["total_episodes"]
                        )
                        normalized["progress"] = self._progress_text(
                            normalized["watched_episodes"],
                            normalized["total_episodes"],
                            True,
                            normalized["watched"],
                        )
                if self._accept_library(normalized):
                    items.append(normalized)
            if len(raw_items) < limit:
                break
            start += limit
        return items

    def _fetch_series_episode_stats(self, service: Any, user_id: str, series_id: Any) -> Dict[str, Any]:
        item_id = self._clean_text(series_id)
        if not item_id:
            return {}
        total = 0
        watched = 0
        size = 0
        paths = []
        start = 0
        limit = 500
        fields = quote("Path,MediaSources,UserData")
        while True:
            url = (
                f"[HOST]emby/Users/{user_id}/Items?ParentId={quote(item_id)}&Recursive=true&IncludeItemTypes=Episode"
                f"&Fields={fields}&EnableTotalRecordCount=false&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            total += len(raw_items)
            for episode in raw_items:
                if (episode.get("UserData") or {}).get("Played"):
                    watched += 1
                path = self._clean_text(episode.get("Path"))
                if path:
                    paths.append(path)
                size += self._media_sources_size(episode.get("MediaSources") or [])
            if len(raw_items) < limit:
                break
            start += limit
        return {"total_episodes": total, "watched_episodes": watched, "size": size, "paths": paths}

    def _normalize_emby_library(self, item: Dict[str, Any], service_info: Any, server_name: str) -> Dict[str, Any]:
        item_id = self._clean_text(item.get("Id"))
        title = self._clean_text(item.get("Name"))
        collection_type = self._clean_text(item.get("CollectionType"))
        if not item_id or not title:
            return {}
        return {
            "id": f"{server_name}:{item_id}",
            "server": server_name,
            "item_id": item_id,
            "title": title,
            "type": collection_type,
            "type_label": self._library_type_label(collection_type),
            "image_url": self._build_image_url(item, service_info, max_height=360, max_width=640),
        }

    def _normalize_emby_item(
        self,
        item: Dict[str, Any],
        service_info: Any,
        server_name: str,
        library_index: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        item_type = self._clean_text(item.get("Type")).lower()
        if item_type not in {"movie", "series"}:
            return {}
        is_series = item_type == "series"
        user_data = item.get("UserData") or {}
        total_episodes = self._to_int(item.get("RecursiveItemCount") or item.get("ChildCount"), 0) if is_series else 1
        unplayed = self._to_int(user_data.get("UnplayedItemCount"), 0)
        watched_episodes = max(total_episodes - unplayed, 0) if is_series else (1 if user_data.get("Played") else 0)
        watched = bool(user_data.get("Played")) or (is_series and total_episodes > 0 and watched_episodes >= total_episodes)
        path = self._clean_text(item.get("Path"))
        library = library_index.get(self._clean_text(item.get("ParentId"))) or {}
        library_name = self._clean_text(library.get("title")) or self._clean_text(item.get("ParentName"))
        return {
            "id": f"{server_name}:{item.get('Id')}",
            "server": server_name,
            "server_type": getattr(service_info, "type", "emby"),
            "item_id": self._clean_text(item.get("Id")),
            "title": self._clean_text(item.get("Name")) or "未命名媒体",
            "type": "series" if is_series else "movie",
            "type_label": "剧集" if is_series else "电影",
            "year": item.get("ProductionYear"),
            "library": library_name,
            "library_id": library.get("id") or "",
            "library_item_id": library.get("item_id") or "",
            "library_type": library.get("type") or "",
            "path": path,
            "path_preview": self._path_preview(path),
            "rating": item.get("CommunityRating") or item.get("CriticRating"),
            "image_url": self._build_image_url(item, service_info),
            "overview": self._clean_text(item.get("Overview")),
            "genres": [self._clean_text(genre) for genre in item.get("Genres") or [] if self._clean_text(genre)],
            "premiere_date": self._format_emby_date(item.get("PremiereDate"))[:10],
            "provider_ids": item.get("ProviderIds") or {},
            "added_at": self._format_emby_date(item.get("DateCreated")),
            "watched": watched,
            "progress": self._progress_text(watched_episodes, total_episodes, is_series, watched),
            "watched_episodes": watched_episodes,
            "total_episodes": total_episodes,
            "size": self._media_sources_size(item.get("MediaSources") or []),
            "episode_paths": [],
        }

    def _accept_library(self, item: Dict[str, Any]) -> bool:
        return self._accept_library_name(item.get("library"))

    def _accept_library_name(self, library_name: Any) -> bool:
        library_names = self._config.get("library_names") or []
        if not library_names:
            return True
        library = self._clean_text(library_name)
        return any(name == library for name in library_names)

    def _build_image_url(self, item: Dict[str, Any], service_info: Any, max_height: int = 500, max_width: int = 340) -> str:
        if not (item.get("ImageTags") or {}).get("Primary"):
            return ""
        base_url = self._service_base_url(service_info)
        if not base_url:
            return ""
        item_id = quote(str(item.get("Id")))
        return f"{base_url.rstrip('/')}/emby/Items/{item_id}/Images/Primary?maxHeight={max_height}&maxWidth={max_width}&quality=90"

    @staticmethod
    def _library_type_label(collection_type: str) -> str:
        return {
            "movies": "电影",
            "tvshows": "电视剧",
            "mixed": "混合媒体",
            "music": "音乐",
            "musicvideos": "音乐视频",
            "homevideos": "家庭视频",
            "boxsets": "合集",
            "books": "图书",
        }.get(collection_type, "媒体库")

    @staticmethod
    def _service_base_url(service_info: Any) -> str:
        candidates = [service_info, getattr(service_info, "config", None), getattr(service_info, "instance", None)]
        keys = ["host", "url", "server", "server_url", "address"]
        for candidate in candidates:
            if not candidate:
                continue
            if isinstance(candidate, dict):
                for key in keys:
                    if candidate.get(key):
                        return str(candidate[key])
                continue
            for key in keys:
                value = getattr(candidate, key, None)
                if value:
                    return str(value)
        return ""

    @staticmethod
    def _media_sources_size(sources: List[Dict[str, Any]]) -> int:
        size = 0
        for source in sources:
            try:
                size += int(source.get("Size") or 0)
            except (TypeError, ValueError):
                continue
        return size

    @staticmethod
    def _format_emby_date(value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        return text.replace("T", " ").replace("Z", "")[:19]

    @staticmethod
    def _progress_text(watched_episodes: int, total_episodes: int, is_series: bool, watched: bool) -> str:
        if is_series:
            return f"{watched_episodes}/{total_episodes}" if total_episodes else "0/0"
        return "已观看" if watched else "未观看"

    def _dedupe_media(self, media: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped = {}
        for item in media:
            key = item.get("id")
            if key:
                deduped[key] = item
        return sorted(deduped.values(), key=lambda item: (item.get("watched") is False, item.get("added_at") or ""))

    def _dedupe_libraries(self, libraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped = {}
        for item in libraries:
            key = item.get("id")
            if key:
                deduped[key] = item
        return sorted(deduped.values(), key=lambda item: (item.get("server") or "", item.get("title") or ""))

    def _build_plan_item(self, media: Dict[str, Any], delete_source: bool) -> Dict[str, Any]:
        records = self._match_transfer_records(media)
        delete_targets: List[Dict[str, Any]] = []
        for record in records:
            dest_fileitem = getattr(record, "dest_fileitem", None)
            src_fileitem = getattr(record, "src_fileitem", None)
            if isinstance(dest_fileitem, dict):
                delete_targets.append(self._target_from_history(record, "dest", dest_fileitem))
            if delete_source and isinstance(src_fileitem, dict):
                delete_targets.append(self._target_from_history(record, "src", src_fileitem))

        status = "ready" if delete_targets else "no_match"
        message = "已匹配整理记录，可执行删除。" if delete_targets else "未匹配到整理记录，已阻止执行真实删除。"
        return {
            "media_id": media.get("id"),
            "title": media.get("title"),
            "type": media.get("type"),
            "type_label": media.get("type_label"),
            "watched": bool(media.get("watched")),
            "size": self._sum_target_size(delete_targets) or int(media.get("size") or 0),
            "matched_transfer_records": [self._transfer_record_summary(record) for record in records],
            "delete_targets": self._dedupe_targets(delete_targets),
            "status": status,
            "message": message,
        }

    def _match_transfer_records(self, media: Dict[str, Any]) -> List[Any]:
        records: List[Any] = []
        title = self._clean_text(media.get("title"))
        tmdbid = self._clean_text((media.get("provider_ids") or {}).get("Tmdb"))
        if tmdbid:
            records.extend(self._query_transfer_by_tmdb(tmdbid, media.get("type")))
        if title:
            records.extend(self._query_transfer_by_title(title))

        path = self._clean_text(media.get("path"))
        matched = []
        for record in self._dedupe_records(records):
            if not bool(getattr(record, "status", True)):
                continue
            if tmdbid and str(getattr(record, "tmdbid", "") or "") == tmdbid:
                matched.append(record)
                continue
            if path and self._path_matches(path, getattr(record, "dest", "")):
                matched.append(record)
                continue
            if title and title.lower() in self._clean_text(getattr(record, "title", "")).lower():
                matched.append(record)
        return self._dedupe_records(matched)

    @staticmethod
    def _dedupe_records(records: List[Any]) -> List[Any]:
        result = []
        seen = set()
        for record in records:
            key = getattr(record, "id", None) or id(record)
            if key in seen:
                continue
            seen.add(key)
            result.append(record)
        return result

    def _query_transfer_by_tmdb(self, tmdbid: str, media_type: str) -> List[Any]:
        oper = TransferHistoryOper()
        records = []
        for mtype in [media_type, media_type.upper() if media_type else "", "MOV" if media_type == "movie" else "TV"]:
            if not mtype:
                continue
            try:
                record = oper.get_by_type_tmdbid(tmdbid=tmdbid, mtype=mtype)
                if isinstance(record, list):
                    records.extend(record)
                elif record:
                    records.append(record)
            except Exception:
                continue
        return records

    def _query_transfer_by_title(self, title: str) -> List[Any]:
        candidates = []
        for source in [TransferHistory, TransferHistoryOper()]:
            if not source or not hasattr(source, "list_by_title"):
                continue
            try:
                candidates.extend(source.list_by_title(title=title, page=1, count=-1, status=True) or [])
                break
            except TypeError:
                try:
                    candidates.extend(source.list_by_title(title=title, page=1, count=-1) or [])
                    break
                except Exception:
                    continue
            except Exception:
                continue
        return candidates

    def _target_from_history(self, record: Any, kind: str, fileitem: Dict[str, Any]) -> Dict[str, Any]:
        path = self._clean_text(getattr(record, kind, "")) or self._clean_text(fileitem.get("path"))
        size = self._to_int(fileitem.get("size") or fileitem.get("size_bytes"), 0)
        return {
            "record_id": getattr(record, "id", None),
            "kind": kind,
            "kind_label": "媒体库文件" if kind == "dest" else "源文件",
            "path": path,
            "path_preview": self._path_preview(path),
            "size": size,
            "fileitem": fileitem,
        }

    def _transfer_record_summary(self, record: Any) -> Dict[str, Any]:
        return {
            "id": getattr(record, "id", None),
            "title": self._clean_text(getattr(record, "title", "")),
            "year": getattr(record, "year", None),
            "type": self._clean_text(getattr(record, "type", "")),
            "src": self._path_preview(getattr(record, "src", "")),
            "dest": self._path_preview(getattr(record, "dest", "")),
            "date": self._clean_text(getattr(record, "date", "")),
        }

    @staticmethod
    def _path_matches(media_path: str, record_path: str) -> bool:
        left = media_path.replace("\\", "/").rstrip("/").lower()
        right = str(record_path or "").replace("\\", "/").rstrip("/").lower()
        return bool(left and right and (left == right or right.startswith(left + "/") or left.startswith(right + "/")))

    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        targets = self._dedupe_targets([target for item in plan.get("items", []) for target in item.get("delete_targets", [])])
        deleted_targets: List[Dict[str, Any]] = []
        failed_targets: List[Dict[str, Any]] = []
        record_status: Dict[Any, bool] = {}
        storage = StorageChain()

        for target in targets:
            record_id = target.get("record_id")
            try:
                result = storage.delete_file(schemas.FileItem(**target["fileitem"]))
                if result is False:
                    raise RuntimeError("StorageChain 返回删除失败")
                deleted_targets.append(target)
                record_status[record_id] = record_status.get(record_id, True) and True
                if target.get("kind") == "src":
                    eventmanager.send_event(EventType.DownloadFileDeleted, {"src": target.get("path")})
            except Exception as err:
                failed = {**target, "error": str(err)}
                failed_targets.append(failed)
                record_status[record_id] = False

        oper = TransferHistoryOper()
        deleted_records = 0
        for record_id, ok in record_status.items():
            if not ok or record_id is None:
                continue
            try:
                oper.delete(record_id)
                deleted_records += 1
            except Exception as err:
                failed_targets.append({"record_id": record_id, "kind": "record", "path": "", "error": f"整理记录删除失败：{err}"})

        reclaim_size = self._sum_target_size(deleted_targets)
        success = not failed_targets
        return {
            "plan_id": plan.get("id"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success" if success else "failed",
            "delete_source": bool(plan.get("delete_source")),
            "reclaim_size": reclaim_size,
            "deleted_records": deleted_records,
            "deleted_targets": deleted_targets,
            "failed_targets": failed_targets,
            "items": [{"title": item.get("title"), "type": item.get("type"), "size": item.get("size")} for item in plan.get("items", [])],
            "message": f"清理完成，删除 {len(deleted_targets)} 个文件，整理记录 {deleted_records} 条。" if success else f"清理未完全成功，失败 {len(failed_targets)} 项，请查看执行记录。",
        }

    def _notify_cleanup_result(self, result: Dict[str, Any]) -> None:
        title = "【媒体库管家】清理完成" if result.get("status") == "success" else "【媒体库管家】清理异常"
        lines = [
            result.get("message", ""),
            f"释放空间：{self._human_size(result.get('reclaim_size'))}",
            f"删除整理记录：{result.get('deleted_records', 0)} 条",
        ]
        if result.get("failed_targets"):
            lines.append("失败项：")
            lines.extend(f"- {item.get('path_preview') or item.get('record_id')}: {item.get('error')}" for item in result["failed_targets"][:5])
        self.post_message(mtype=NotificationType.MediaServer, title=title, text="\n".join(lines))

    def _notify_disk_warning(self, snapshot: Dict[str, Any]) -> None:
        if not self._config.get("disk_warning_enabled") or not self._config.get("notify_enabled"):
            return
        disk_status = self._disk_status(snapshot)
        risks = [item for item in disk_status if item.get("warning")]
        if not risks:
            return
        today = datetime.now().strftime("%Y-%m-%d")
        if self.get_data(self.DATA_KEY_LAST_DISK_WARNING) == today:
            return
        recommendations = self._build_recommendations(snapshot)[:8]
        lines = ["检测到磁盘容量低于阈值："]
        for risk in risks:
            title = risk.get("display_name") or risk.get("mount_point") or risk.get("path")
            lines.append(f"- {title} 剩余 {self._human_size(risk['free'])}（{risk['free_percent']}%）")
        if recommendations:
            lines.append("\n建议优先检查：")
            for item in recommendations:
                lines.append(f"- {item['title']}：{item['reason']}，预计 {self._human_size(item.get('size'))}")
        self.post_message(mtype=NotificationType.MediaServer, title="【媒体库管家】磁盘容量告警", text="\n".join(lines))
        self.save_data(self.DATA_KEY_LAST_DISK_WARNING, today)

    def _load_history(self) -> List[Dict[str, Any]]:
        history = self.get_data(self.DATA_KEY_HISTORY) or []
        return history if isinstance(history, list) else []

    def _load_snapshot(self) -> Dict[str, Any]:
        snapshot = self.get_data(self.DATA_KEY_SNAPSHOT) or {}
        return snapshot if isinstance(snapshot, dict) else {}

    def _build_summary(self, snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        snapshot = snapshot or self._load_snapshot()
        media = snapshot.get("media", [])
        libraries = snapshot.get("libraries", [])
        movies = [item for item in media if item.get("type") == "movie"]
        series = [item for item in media if item.get("type") == "series"]
        disk_status = self._disk_status(snapshot)
        return {
            "libraries": len(libraries) or len({item.get("library") for item in media if item.get("library")}),
            "movies": len(movies),
            "series": len(series),
            "episodes": sum(int(item.get("total_episodes") or 0) for item in series),
            "watched_series": len([item for item in series if item.get("watched")]),
            "unwatched_large_series": len([item for item in series if not item.get("watched") and int(item.get("size") or 0) > 0]),
            "estimated_reclaim_size": sum(int(item.get("size") or 0) for item in media if item.get("watched")),
            "disk_warning": any(item.get("warning") for item in disk_status),
            "disk_status": disk_status,
            "last_scan_at": snapshot.get("scanned_at"),
            "connection_state": "connected" if media else "not_scanned",
            "errors": snapshot.get("errors", []),
        }

    def _build_recommendations(self, snapshot: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        snapshot = snapshot or self._load_snapshot()
        media = snapshot.get("media", [])
        recommendations = []
        for item in media:
            if item.get("type") == "series" and item.get("watched"):
                recommendations.append({**item, "reason": "已看完剧集", "message": "已观看全集，适合优先释放空间。"})
            elif item.get("type") == "series" and not item.get("watched"):
                recommendations.append({**item, "reason": "入库较久未看", "message": "长期未观看，可结合容量压力决定是否清理。"})
            elif item.get("type") == "movie" and item.get("watched"):
                recommendations.append({**item, "reason": "已看完电影", "message": "已观看电影，可按需清理。"})
        return sorted(recommendations, key=lambda item: (item.get("watched") is False, -(int(item.get("size") or 0)), item.get("added_at") or ""))[:30]

    def _disk_status(self, snapshot: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        disks = self._media_disks(snapshot)
        status = []
        for disk in disks:
            path = disk["path"]
            try:
                usage = shutil.disk_usage(path)
                free_percent = round(usage.free * 100 / usage.total, 2) if usage.total else 0
                warning = usage.free <= self._config["disk_warning_free_gb"] * 1024 ** 3 or free_percent <= self._config["disk_warning_free_percent"]
                status.append(
                    {
                        "path": path,
                        "display_name": disk.get("display_name") or path,
                        "mount_point": disk.get("mount_point") or path,
                        "device": disk.get("device") or "",
                        "source_paths": disk.get("source_paths") or [],
                        "total": usage.total,
                        "free": usage.free,
                        "free_percent": free_percent,
                        "warning": warning,
                    }
                )
            except Exception as err:
                status.append(
                    {
                        "path": path,
                        "display_name": disk.get("display_name") or path,
                        "mount_point": disk.get("mount_point") or path,
                        "device": disk.get("device") or "",
                        "source_paths": disk.get("source_paths") or [],
                        "total": 0,
                        "free": 0,
                        "free_percent": 0,
                        "warning": False,
                        "error": str(err),
                    }
                )
        return status

    def _media_disks(self, snapshot: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        snapshot = snapshot or self._load_snapshot()
        paths = []
        for item in snapshot.get("media", []):
            if item.get("path"):
                paths.append(item.get("path"))
            paths.extend(item.get("episode_paths") or [])
        if not paths:
            value = getattr(settings, "LIBRARY_PATH", "")
            if value:
                paths.append(str(value))

        disks: Dict[Any, Dict[str, Any]] = {}
        for path in paths:
            disk_path = self._existing_disk_path(path)
            if not disk_path:
                continue
            disk = self._disk_identity(disk_path)
            if not disk:
                continue
            key = disk["key"]
            if key not in disks:
                disks[key] = {**disk, "source_paths": []}
            disks[key]["source_paths"].append(self._path_preview(path))
        return list(disks.values())

    def _existing_disk_path(self, path: Any) -> str:
        text = self._clean_text(path)
        if not text:
            return ""
        current = Path(text)
        if current.exists():
            return str(current if current.is_dir() else current.parent)
        for parent in current.parents:
            if parent.exists():
                return str(parent)
        return ""

    def _disk_identity(self, path: str) -> Dict[str, Any]:
        mount_point, device = self._mount_info(path)
        if not mount_point:
            return {}
        try:
            stat = os.stat(mount_point)
        except OSError:
            return {}
        return {
            "key": stat.st_dev,
            "path": mount_point,
            "mount_point": mount_point,
            "device": device,
            "display_name": self._volume_display_name(mount_point, device),
        }

    def _mount_info(self, path: str) -> Tuple[str, str]:
        if os.name == "nt":
            mount_point = Path(path).anchor or path
            return mount_point, mount_point.rstrip("\\/")
        mount_points = self._linux_mount_points()
        normalized = os.path.realpath(path)
        for mount_point, device in mount_points:
            real_mount = os.path.realpath(mount_point)
            if normalized == real_mount or normalized.startswith(real_mount.rstrip("/") + "/"):
                return mount_point, device
        return "/", ""

    @staticmethod
    def _linux_mount_points() -> List[Tuple[str, str]]:
        mountinfo = Path("/proc/self/mountinfo")
        if not mountinfo.exists():
            return [("/", "")]
        points: List[Tuple[str, str]] = []
        try:
            for line in mountinfo.read_text(encoding="utf-8", errors="ignore").splitlines():
                parts = line.split()
                if len(parts) < 10 or "-" not in parts:
                    continue
                separator = parts.index("-")
                mount_point = MediaLibraryKeeper._decode_mountinfo_path(parts[4])
                device = parts[separator + 2] if len(parts) > separator + 2 else ""
                if mount_point:
                    points.append((mount_point, device))
        except Exception:
            return [("/", "")]
        return sorted(points, key=lambda item: len(item[0]), reverse=True) or [("/", "")]

    @staticmethod
    def _decode_mountinfo_path(path: str) -> str:
        return path.replace("\\040", " ").replace("\\011", "\t").replace("\\012", "\n").replace("\\134", "\\")

    def _volume_display_name(self, mount_point: str, device: str = "") -> str:
        if os.name == "nt":
            label = self._windows_volume_label(mount_point)
            return label or mount_point.rstrip("\\/") or mount_point
        label = self._linux_volume_label(device)
        if label:
            return label
        return self._mount_name(mount_point)

    @staticmethod
    def _windows_volume_label(mount_point: str) -> str:
        try:
            import ctypes

            root = str(Path(mount_point).anchor or mount_point)
            volume_name = ctypes.create_unicode_buffer(261)
            result = ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(root),
                volume_name,
                len(volume_name),
                None,
                None,
                None,
                None,
                0,
            )
            return volume_name.value if result and volume_name.value else ""
        except Exception:
            return ""

    @staticmethod
    def _linux_volume_label(device: str) -> str:
        if not device or not device.startswith("/dev/"):
            return ""
        label_dir = Path("/dev/disk/by-label")
        if not label_dir.exists():
            return ""
        try:
            device_real = os.path.realpath(device)
            for label in label_dir.iterdir():
                if os.path.realpath(label) == device_real:
                    return label.name
        except Exception:
            return ""
        return ""

    @staticmethod
    def _mount_name(mount_point: str) -> str:
        normalized = mount_point.replace("\\", "/").strip("/")
        if not normalized:
            return "根目录"
        parts = [part for part in normalized.split("/") if part]
        if not parts:
            return mount_point
        if parts[0] in {"mnt", "media", "run", "volume1", "volume2", "volumes"} and len(parts) > 1:
            return parts[1]
        return parts[0]

    @staticmethod
    def _capabilities() -> Dict[str, Any]:
        return {
            "emby_scan": True,
            "transfer_history_match": True,
            "storage_delete": True,
            "ai_suggestions": False,
            "notification": True,
        }

    @staticmethod
    def _sum_target_size(targets: List[Dict[str, Any]]) -> int:
        return sum(int(target.get("size") or 0) for target in targets)

    def _sum_unique_target_size(self, plan_items: List[Dict[str, Any]]) -> int:
        return self._sum_target_size(self._dedupe_targets([target for item in plan_items for target in item.get("delete_targets", [])]))

    @staticmethod
    def _dedupe_targets(targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for target in targets:
            key = (target.get("record_id"), target.get("kind"), target.get("path"))
            if key in seen:
                continue
            seen.add(key)
            result.append(target)
        return result

    @staticmethod
    def _plan_message(status: str, items: List[Dict[str, Any]]) -> str:
        if status == "ready":
            return "清理计划已生成，所有条目均匹配到整理记录。执行前请再次确认删除范围。"
        blocked = len([item for item in items if item.get("status") != "ready"])
        return f"清理计划存在 {blocked} 个未匹配整理记录的条目，已阻止真实删除。"

    @staticmethod
    def _path_preview(path: Any) -> str:
        text = str(path or "").strip()
        if len(text) <= 80:
            return text
        return "..." + text[-77:]

    @staticmethod
    def _human_size(value: Any) -> str:
        size = float(value or 0)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{size:.1f} EB"

    @eventmanager.register(EventType.PluginReload)
    def reload(self, event: Event):
        if event and event.event_data and event.event_data.get("plugin_id") == self.__class__.__name__:
            register_plugin_api(plugin_id=self.__class__.__name__)
