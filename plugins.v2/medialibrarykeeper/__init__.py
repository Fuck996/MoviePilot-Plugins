import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from apscheduler.triggers.cron import CronTrigger
from fastapi import Body, Depends, HTTPException, Response, status

from app import schemas
from app.api.endpoints.plugin import register_plugin_api
from app.chain.storage import StorageChain
from app.core.config import settings
from app.core.event import Event, eventmanager
from app.core.security import verify_resource_token
from app.db.transferhistory_oper import TransferHistoryOper
from app.helper.directory import DirectoryHelper
from app.helper.downloader import DownloaderHelper
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
    plugin_version = "0.3.17"
    plugin_author = "fuck996"
    author_url = "https://github.com/Fuck996"
    plugin_config_prefix = "medialibrarykeeper_"
    plugin_order = 48
    auth_level = 1

    DATA_KEY_HISTORY = "history"
    DATA_KEY_PENDING_PLAN = "pending_plan"
    DATA_KEY_SNAPSHOT = "snapshot"
    DATA_KEY_LAST_DISK_WARNING = "last_disk_warning"
    SUPPORTED_DOWNLOADER_TYPES = {"qbittorrent", "transmission"}
    LINK_TRANSFER_TYPES = {"link", "softlink"}

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
                "kwargs": {"notify_disk_warning": True, "build_cleanup_batch": True},
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
                "path": "/cleanup/scan",
                "endpoint": self.scan_cleanup_plan_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "按清理规则扫描并生成批次",
            },
            {
                "path": "/cleanup/plan",
                "endpoint": self.create_cleanup_plan_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "生成清理计划",
            },
            {
                "path": "/cleanup/plan/delete",
                "endpoint": self.delete_cleanup_plan_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "删除当前清理批次",
            },
            {
                "path": "/cleanup/execute",
                "endpoint": self.execute_cleanup_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "执行清理计划",
            },
            {
                "path": "/cleanup/plan/items",
                "endpoint": self.update_cleanup_plan_items_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "调整清理批次条目",
            },
            {
                "path": "/image",
                "endpoint": self.get_image_api,
                "methods": ["GET"],
                "allow_anonymous": True,
                "summary": "Proxy Emby image",
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
        snapshot = self._with_proxy_image_urls(self._load_snapshot())
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
                "downloader_options": self._downloader_options(),
                "cache": self._cache_meta(snapshot),
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

    def scan_cleanup_plan_api(self) -> schemas.Response:
        try:
            snapshot = self.scan_library(notify_disk_warning=True)
            plan = self._create_scheduled_cleanup_batch(
                snapshot,
                source="rule_scan",
                overwrite_sources={"scheduled", "rule_scan"},
            )
            status_data = self.get_status().data
            if plan:
                return schemas.Response(success=True, message="已按当前清理规则生成待审核批次", data=status_data)
            pending_plan = (status_data or {}).get("pending_plan") or {}
            if pending_plan and pending_plan.get("source") not in {"scheduled", "rule_scan"}:
                return schemas.Response(success=True, message="当前已有手动清理批次，已保留原批次未覆盖", data=status_data)
            return schemas.Response(success=True, message="当前清理规则未命中媒体", data=status_data)
        except Exception as err:
            logger.error(f"媒体库管家规则扫描失败：{err}")
            return schemas.Response(success=False, message=str(err), data=self.get_status().data)

    def scan_library(self, notify_disk_warning: bool = False, build_cleanup_batch: bool = False) -> Dict[str, Any]:
        services = self._active_emby_services()
        if not services:
            raise RuntimeError("没有可用的 Emby 媒体服务器，请先在 MoviePilot 媒体服务器中完成配置。")

        libraries: List[Dict[str, Any]] = []
        media: List[Dict[str, Any]] = []
        errors: List[str] = []
        for server_name, service_info in services.items():
            service = service_info.instance
            try:
                user_id = self._resolve_emby_user_id(service, service_info)
                if not user_id:
                    errors.append(f"{server_name} 未解析到 Emby 用户，请检查 MoviePilot 媒体服务器用户名配置。")
                    continue
                server_libraries = self._fetch_emby_libraries(service, service_info, server_name, user_id)
                libraries.extend(server_libraries)
                for library in server_libraries:
                    media.extend(self._fetch_emby_items(service, service_info, server_name, user_id, library))
            except Exception as err:
                logger.error(f"媒体库管家读取 Emby {server_name} 失败：{err}")
                errors.append(f"{server_name}: {err}")

        media_items = self._attach_media_volume_info(self._dedupe_media(media))
        snapshot = {
            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "libraries": self._dedupe_libraries(libraries),
            "media": media_items,
            "errors": errors,
        }
        self.save_data(self.DATA_KEY_SNAPSHOT, snapshot)

        if notify_disk_warning:
            self._notify_disk_warning(snapshot)
        if build_cleanup_batch:
            self._create_scheduled_cleanup_batch(snapshot)
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
        plan = self._build_cleanup_plan([media_index[item_id] for item_id in selected_ids], delete_source, source="manual")
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        return schemas.Response(success=True, data={"plan": plan, "status": self.get_status().data})

    def update_cleanup_plan_items_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        plan_id = self._clean_text(payload.get("plan_id"))
        action = self._clean_text(payload.get("action")).lower()
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        if not plan_id or pending_plan.get("id") != plan_id:
            return schemas.Response(success=False, message="清理批次不存在或已失效")
        if action not in {"add", "remove"}:
            return schemas.Response(success=False, message="不支持的批次调整动作")

        item_ids = [self._clean_text(item) for item in payload.get("item_ids") or [] if self._clean_text(item)]
        if not item_ids:
            return schemas.Response(success=False, message="请选择要调整的媒体条目")

        snapshot = self._load_snapshot()
        media_index = {item.get("id"): item for item in snapshot.get("media", [])}
        current_ids = [item.get("media_id") for item in pending_plan.get("items", []) if item.get("media_id")]
        if action == "remove":
            next_ids = [item_id for item_id in current_ids if item_id not in set(item_ids)]
        else:
            missing = [item_id for item_id in item_ids if item_id not in media_index]
            if missing:
                return schemas.Response(success=False, message="所选媒体不在最近一次扫描结果中，请先重新扫描媒体库。")
            next_ids = list(dict.fromkeys([*current_ids, *item_ids]))

        media_items = [media_index[item_id] for item_id in next_ids if item_id in media_index]
        plan = self._build_cleanup_plan(
            media_items,
            bool(pending_plan.get("delete_source")),
            source=pending_plan.get("source") or "manual",
            criteria=pending_plan.get("criteria"),
            plan_id=pending_plan.get("id"),
            created_at=pending_plan.get("created_at"),
        )
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        return schemas.Response(success=True, data={"plan": plan, "status": self.get_status().data})

    def delete_cleanup_plan_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        plan_id = self._clean_text(payload.get("plan_id"))
        confirm = bool(payload.get("confirm"))
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        if not plan_id or pending_plan.get("id") != plan_id:
            return schemas.Response(success=False, message="清理批次不存在或已失效")
        if not confirm:
            return schemas.Response(success=False, message="删除批次前需要页面确认。")
        self.save_data(self.DATA_KEY_PENDING_PLAN, None)
        return schemas.Response(success=True, message="已删除当前清理批次", data=self.get_status().data)

    def execute_cleanup_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        plan_id = self._clean_text(payload.get("plan_id"))
        confirm = bool(payload.get("confirm"))
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        if not plan_id or pending_plan.get("id") != plan_id:
            return schemas.Response(success=False, message="清理计划不存在或已失效")
        if not confirm:
            return schemas.Response(success=False, message="执行清理前需要在页面确认删除范围。")
        if self._plan_ready_count(pending_plan) <= 0:
            return schemas.Response(success=False, message=pending_plan.get("message") or "清理计划没有可执行条目。")

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

    def get_image_api(
        self,
        server: str,
        item_id: str,
        image_type: str = "Primary",
        max_height: int = 500,
        max_width: int = 340,
        _: Any = Depends(verify_resource_token),
    ):
        server_name = self._clean_text(server)
        media_item_id = self._clean_text(item_id)
        image_name = self._clean_text(image_type) or "Primary"
        if not server_name or not media_item_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少媒体服务器或媒体 ID")
        if image_name not in {"Primary", "Backdrop", "Logo", "Thumb", "Banner"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的图片类型")

        service_info = MediaServerHelper().get_service(name=server_name, type_filter="emby")
        service = getattr(service_info, "instance", None) if service_info else None
        if not service or not hasattr(service, "get_data"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="媒体服务器不可用")

        height = self._bound_image_size(max_height)
        width = self._bound_image_size(max_width)
        url = (
            f"[HOST]Items/{quote(media_item_id, safe='')}/Images/{quote(image_name, safe='')}"
            f"?api_key=[APIKEY]&maxHeight={height}&maxWidth={width}&quality=90"
        )
        response = service.get_data(url)
        content = getattr(response, "content", None) if response else None
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在或无法读取")

        media_type = (getattr(response, "headers", {}) or {}).get("content-type") or "image/jpeg"
        return Response(
            content=content,
            media_type=media_type,
            headers={"Cache-Control": "private, max-age=86400"},
        )

    def _with_proxy_image_urls(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(snapshot, dict):
            return {}
        patched = dict(snapshot)
        image_sizes = {
            "libraries": (360, 640),
            "media": (500, 340),
        }
        for key, (height, width) in image_sizes.items():
            rows = []
            for row in snapshot.get(key, []) or []:
                if not isinstance(row, dict):
                    continue
                item = dict(row)
                if item.get("image_url") and item.get("server") and item.get("item_id"):
                    item["image_url"] = self._build_proxy_image_url(
                        str(item["server"]),
                        str(item["item_id"]),
                        max_height=height,
                        max_width=width,
                    )
                rows.append(item)
            patched[key] = rows
        return patched

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
            "downloaders": [],
            "delete_seed_tasks": False,
            "library_names": [],
            "cleanup_libraries": [],
            "cleanup_rules": [MediaLibraryKeeper._default_cleanup_rule()],
            "cleanup_operator": "and",
            "cleanup_watch_state": "any",
            "cleanup_unwatched_days": 0,
            "cleanup_watched": False,
            "cleanup_min_size_gb": 0,
            "cleanup_max_rating": 0,
        }

    @classmethod
    def _normalize_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        defaults = cls._default_config()
        normalized = {**defaults, **(config or {})}
        raw_config = config or {}
        for key in ["enabled", "show_sidebar_nav", "notify_enabled", "disk_warning_enabled", "ai_suggestions", "default_delete_source", "delete_seed_tasks"]:
            normalized[key] = cls._to_bool(normalized.get(key, defaults[key]))
        normalized["disk_warning_free_gb"] = max(cls._to_int(normalized.get("disk_warning_free_gb"), 200), 0)
        normalized["disk_warning_free_percent"] = max(cls._to_int(normalized.get("disk_warning_free_percent"), 10), 0)
        normalized["scan_cron"] = cls._clean_text(normalized.get("scan_cron")) or defaults["scan_cron"]
        for key in ["mediaservers", "downloaders", "cleanup_libraries"]:
            normalized[key] = cls._to_list(normalized.get(key))
        normalized["library_names"] = []
        normalized["cleanup_rules"] = cls._normalize_cleanup_rules(raw_config)
        first_rule = normalized["cleanup_rules"][0] if normalized["cleanup_rules"] else cls._default_cleanup_rule()
        normalized["cleanup_operator"] = first_rule["operator"]
        normalized["cleanup_watch_state"] = first_rule["watch_state"]
        normalized["cleanup_watched"] = first_rule["watch_state"] == "watched"
        normalized["cleanup_unwatched_days"] = first_rule["unwatched_days"]
        normalized["cleanup_min_size_gb"] = first_rule["min_size_gb"]
        normalized["cleanup_max_rating"] = first_rule["max_rating"]
        return normalized

    @staticmethod
    def _default_cleanup_rule() -> Dict[str, Any]:
        return {
            "operator": "and",
            "watch_state": "any",
            "unwatched_days": 0,
            "min_size_gb": 0,
            "max_rating": 0,
        }

    @classmethod
    def _normalize_cleanup_rules(cls, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_rules = config.get("cleanup_rules")
        if isinstance(raw_rules, list) and raw_rules:
            rules = raw_rules
        else:
            rules = [{
                "operator": config.get("cleanup_operator"),
                "watch_state": config.get("cleanup_watch_state"),
                "watched": config.get("cleanup_watched"),
                "unwatched_days": config.get("cleanup_unwatched_days"),
                "min_size_gb": config.get("cleanup_min_size_gb"),
                "max_rating": config.get("cleanup_max_rating"),
            }]
        return [cls._normalize_cleanup_rule(rule) for rule in rules if isinstance(rule, dict)]

    @classmethod
    def _normalize_cleanup_rule(cls, rule: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {**cls._default_cleanup_rule(), **(rule or {})}
        operator = cls._clean_text(normalized.get("operator")).lower()
        normalized["operator"] = operator if operator in {"and", "or"} else "and"
        watch_state = cls._clean_text(normalized.get("watch_state")).lower()
        if watch_state not in {"any", "watched", "unwatched"}:
            watch_state = "watched" if cls._to_bool(normalized.get("watched")) else "any"
        normalized["watch_state"] = watch_state
        normalized["unwatched_days"] = max(cls._to_int(normalized.get("unwatched_days"), 0), 0)
        normalized["min_size_gb"] = max(cls._to_int(normalized.get("min_size_gb"), 0), 0)
        normalized["max_rating"] = max(cls._to_float(normalized.get("max_rating"), 0), 0)
        return normalized

    @staticmethod
    def _to_list(value: Any) -> List[str]:
        if isinstance(value, str):
            return [line.strip() for line in value.splitlines() if line.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item or "").strip()]
        return []

    @staticmethod
    def _to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    @classmethod
    def _is_played_user_data(cls, user_data: Dict[str, Any]) -> bool:
        if not isinstance(user_data, dict):
            return False
        if cls._to_bool(user_data.get("Played")):
            return True
        if cls._to_int(user_data.get("PlayCount"), 0) > 0:
            return True
        if cls._clean_text(user_data.get("LastPlayedDate")):
            return True
        return cls._to_float(user_data.get("PlayedPercentage"), 0) >= 90

    @classmethod
    def _has_play_activity_user_data(cls, user_data: Dict[str, Any]) -> bool:
        if cls._is_played_user_data(user_data):
            return True
        if not isinstance(user_data, dict):
            return False
        if cls._to_int(user_data.get("PlaybackPositionTicks"), 0) > 0:
            return True
        return cls._to_float(user_data.get("PlayedPercentage"), 0) > 0

    @staticmethod
    def _to_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_float(value: Any, default: float = 0) -> float:
        try:
            return float(value)
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

    def _downloader_options(self) -> List[Dict[str, str]]:
        options = []
        try:
            services = DownloaderHelper().get_services() or {}
            for name, service_info in services.items():
                dtype = self._clean_text(getattr(service_info, "type", "")).lower()
                if dtype not in self.SUPPORTED_DOWNLOADER_TYPES:
                    continue
                title = f"{name} ({self._downloader_type_label(dtype)})"
                options.append({"title": title, "value": name})
        except Exception as err:
            logger.warning(f"媒体库管家读取下载器配置失败：{err}")
        return options

    @staticmethod
    def _downloader_type_label(dtype: str) -> str:
        return {
            "qbittorrent": "QB",
            "transmission": "Transmission",
        }.get(dtype, dtype)

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

    def _resolve_emby_user_id(self, service: Any, service_info: Any) -> str:
        user_id = self._clean_text(getattr(service, "user", ""))
        if user_id:
            return user_id

        users = self._fetch_emby_users(service)
        username = self._clean_text(getattr(service, "_username", ""))
        config = getattr(service_info, "config", None)
        config_data = getattr(config, "config", {}) or {}
        username = username or self._clean_text(config_data.get("username"))
        if username:
            for user in users:
                if self._clean_text(user.get("Name")) == username:
                    return self._clean_text(user.get("Id"))
        for user in users:
            if (user.get("Policy") or {}).get("IsAdministrator"):
                return self._clean_text(user.get("Id"))
        return self._clean_text((users[0] or {}).get("Id")) if users else ""

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
        library: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        library_item_id = self._clean_text(library.get("item_id"))
        if not library_item_id:
            return []
        items: List[Dict[str, Any]] = []
        start = 0
        limit = 200
        include_types = self._library_include_types(library.get("type"))
        fields = quote(
            "DateCreated,Path,Genres,ProviderIds,Overview,PrimaryImageAspectRatio,BasicSyncInfo,UserData,"
            "ChildCount,RecursiveItemCount,ProductionYear,CommunityRating,CriticRating,SortName,MediaSources,"
            "ParentId,PremiereDate,RunTimeTicks,ImageTags,BackdropImageTags,UserDataPlayCount,"
            "UserDataLastPlayedDate"
        )
        while True:
            url = (
                f"[HOST]emby/Users/{user_id}/Items?ParentId={quote(library_item_id)}&Recursive=true"
                f"&IncludeItemTypes={include_types}"
                f"&Fields={fields}&ImageTypeLimit=1&EnableTotalRecordCount=false"
                f"&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            for item in raw_items:
                normalized = self._normalize_emby_item(item, service_info, server_name, library)
                if not normalized:
                    continue
                if normalized.get("type") == "series":
                    stats = self._fetch_series_episode_stats(service, user_id, normalized.get("item_id"))
                    if stats:
                        normalized["total_episodes"] = stats["total_episodes"] or normalized.get("total_episodes", 0)
                        normalized["watched_episodes"] = stats["watched_episodes"]
                        normalized["started_episodes"] = stats.get("started_episodes", normalized["watched_episodes"])
                        normalized["size"] = stats["size"] or normalized.get("size", 0)
                        normalized["episode_paths"] = stats["paths"]
                        normalized["last_episode_added_at"] = stats.get("last_episode_added_at") or normalized.get("last_episode_added_at", "")
                        normalized["last_watched_at"] = stats.get("last_watched_at") or normalized.get("last_watched_at", "")
                        normalized["watched"] = (
                            normalized["total_episodes"] > 0
                            and normalized["watched_episodes"] >= normalized["total_episodes"]
                        )
                        normalized["watch_state"] = self._watch_state(
                            normalized["watched_episodes"],
                            normalized["total_episodes"],
                            True,
                            normalized["watched"],
                            normalized.get("started_episodes", 0),
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

    @staticmethod
    def _library_include_types(collection_type: Any) -> str:
        library_type = str(collection_type or "").strip().lower()
        if library_type == "movies":
            return "Movie"
        if library_type == "tvshows":
            return "Series"
        return "Movie,Series"

    def _fetch_series_episode_stats(self, service: Any, user_id: str, series_id: Any) -> Dict[str, Any]:
        item_id = self._clean_text(series_id)
        if not item_id:
            return {}
        total = 0
        watched = 0
        started = 0
        size = 0
        paths = []
        start = 0
        limit = 500
        fields = quote("Path,MediaSources,UserData,DateCreated,UserDataPlayCount,UserDataLastPlayedDate")
        last_episode_added_at = ""
        last_watched_at = ""
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
                user_data = episode.get("UserData") or {}
                if self._is_played_user_data(user_data):
                    watched += 1
                if self._has_play_activity_user_data(user_data):
                    started += 1
                last_episode_added_at = self._max_date_text(last_episode_added_at, self._format_emby_date(episode.get("DateCreated")))
                last_watched_at = self._max_date_text(last_watched_at, self._format_emby_date(user_data.get("LastPlayedDate")))
                path = self._clean_text(episode.get("Path"))
                if path:
                    paths.append(path)
                size += self._media_sources_size(episode.get("MediaSources") or [])
            if len(raw_items) < limit:
                break
            start += limit
        return {
            "total_episodes": total,
            "watched_episodes": watched,
            "started_episodes": started,
            "size": size,
            "paths": paths,
            "last_episode_added_at": last_episode_added_at,
            "last_watched_at": last_watched_at,
        }

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
            "image_url": self._build_image_url(item, server_name, max_height=360, max_width=640),
        }

    def _normalize_emby_item(
        self,
        item: Dict[str, Any],
        service_info: Any,
        server_name: str,
        library: Dict[str, Any],
    ) -> Dict[str, Any]:
        item_type = self._clean_text(item.get("Type")).lower()
        if item_type not in {"movie", "series"}:
            return {}
        is_series = item_type == "series"
        user_data = item.get("UserData") or {}
        total_episodes = self._to_int(item.get("RecursiveItemCount") or item.get("ChildCount"), 0) if is_series else 1
        played = self._is_played_user_data(user_data)
        if is_series:
            if played:
                watched_episodes = total_episodes
            elif user_data.get("UnplayedItemCount") is not None:
                unplayed = self._to_int(user_data.get("UnplayedItemCount"), 0)
                watched_episodes = max(total_episodes - unplayed, 0)
            else:
                watched_episodes = 0
        else:
            watched_episodes = 1 if played else 0
        watched = played or (is_series and total_episodes > 0 and watched_episodes >= total_episodes)
        started_episodes = watched_episodes if is_series else (1 if self._has_play_activity_user_data(user_data) else 0)
        watch_state = self._watch_state(watched_episodes, total_episodes, is_series, watched, started_episodes)
        path = self._clean_text(item.get("Path"))
        library_name = self._clean_text(library.get("title")) or self._clean_text(item.get("ParentName"))
        added_at = self._format_emby_date(item.get("DateCreated"))
        last_watched_at = self._format_emby_date(user_data.get("LastPlayedDate"))
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
            "image_url": self._build_image_url(item, server_name),
            "overview": self._clean_text(item.get("Overview")),
            "genres": [self._clean_text(genre) for genre in item.get("Genres") or [] if self._clean_text(genre)],
            "premiere_date": self._format_emby_date(item.get("PremiereDate"))[:10],
            "provider_ids": item.get("ProviderIds") or {},
            "added_at": added_at,
            "last_episode_added_at": added_at,
            "last_watched_at": last_watched_at,
            "watched": watched,
            "watch_state": watch_state,
            "progress": self._progress_text(watched_episodes, total_episodes, is_series, watched),
            "watched_episodes": watched_episodes,
            "started_episodes": started_episodes,
            "total_episodes": total_episodes,
            "size": self._media_sources_size(item.get("MediaSources") or []),
            "episode_paths": [],
        }

    def _accept_library(self, item: Dict[str, Any]) -> bool:
        return self._accept_library_name(item.get("library"))

    def _accept_library_name(self, library_name: Any) -> bool:
        return True

    def _build_image_url(self, item: Dict[str, Any], server_name: str, max_height: int = 500, max_width: int = 340) -> str:
        if not (item.get("ImageTags") or {}).get("Primary"):
            return ""
        item_id = self._clean_text(item.get("Id"))
        if not server_name or not item_id:
            return ""
        return self._build_proxy_image_url(server_name, item_id, max_height=max_height, max_width=max_width)

    def _build_proxy_image_url(self, server_name: str, item_id: str, max_height: int = 500, max_width: int = 340) -> str:
        server = self._clean_text(server_name)
        media_item_id = self._clean_text(item_id)
        if not server or not media_item_id:
            return ""
        return (
            f"plugin/{self.__class__.__name__}/image?"
            f"server={quote(server, safe='')}&item_id={quote(media_item_id, safe='')}"
            f"&image_type=Primary&max_height={self._bound_image_size(max_height)}"
            f"&max_width={self._bound_image_size(max_width)}"
        )

    @staticmethod
    def _bound_image_size(value: Any) -> int:
        try:
            size = int(value)
        except (TypeError, ValueError):
            return 500
        return min(max(size, 1), 2000)

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
    def _max_date_text(left: Any, right: Any) -> str:
        left_text = str(left or "").strip()
        right_text = str(right or "").strip()
        if not left_text:
            return right_text
        if not right_text:
            return left_text
        return max(left_text, right_text)

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        text = str(value or "").strip()
        if not text:
            return None
        for fmt, length in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d", 10)):
            try:
                return datetime.strptime(text[:length], fmt)
            except ValueError:
                continue
        return None

    def _inactive_days(self, item: Dict[str, Any]) -> int:
        last_active = (
            self._parse_date(item.get("last_watched_at"))
            or self._parse_date(item.get("last_episode_added_at"))
            or self._parse_date(item.get("added_at"))
        )
        if not last_active:
            return 0
        return max((datetime.now() - last_active).days, 0)

    @staticmethod
    def _progress_text(watched_episodes: int, total_episodes: int, is_series: bool, watched: bool) -> str:
        if is_series:
            return f"{watched_episodes}/{total_episodes}" if total_episodes else "0/0"
        return "已观看" if watched else "未观看"

    @staticmethod
    def _watch_state(
        watched_episodes: int,
        total_episodes: int,
        is_series: bool,
        watched: bool,
        started_episodes: int = 0,
    ) -> str:
        if watched:
            return "watched"
        if is_series:
            return "watching" if watched_episodes > 0 or started_episodes > 0 else "unwatched"
        return "watching" if started_episodes > 0 else "unwatched"

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

    def _build_cleanup_plan(
        self,
        media_items: List[Dict[str, Any]],
        delete_source: bool,
        source: str = "manual",
        criteria: Optional[Dict[str, Any]] = None,
        plan_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        batch_id = plan_id or datetime.now().strftime("%Y%m%d%H%M%S")
        plan_items = [self._build_plan_item(media, delete_source) for media in media_items]
        ready_count = len([item for item in plan_items if item.get("status") == "ready"])
        estimated_size = self._sum_unique_target_size(plan_items)
        plan_status = "ready" if plan_items and ready_count == len(plan_items) else "empty" if not plan_items else "blocked"
        return {
            "id": batch_id,
            "batch_id": batch_id,
            "created_at": created_at or now_text,
            "updated_at": now_text,
            "source": source,
            "source_label": self._plan_source_label(source),
            "criteria": criteria or {},
            "delete_source": delete_source,
            "items": plan_items,
            "estimated_reclaim_size": estimated_size,
            "ready_count": ready_count,
            "status": plan_status,
            "message": self._plan_message(plan_status, plan_items),
        }

    @staticmethod
    def _plan_ready_count(plan: Dict[str, Any]) -> int:
        return len([item for item in plan.get("items", []) if item.get("status") == "ready"])

    @staticmethod
    def _plan_source_label(source: str) -> str:
        return {
            "scheduled": "定时计划",
            "rule_scan": "规则扫描",
            "manual": "手动选择",
        }.get(source, "手动选择")

    def _create_scheduled_cleanup_batch(
        self,
        snapshot: Dict[str, Any],
        source: str = "scheduled",
        overwrite_sources: Optional[set] = None,
    ) -> Optional[Dict[str, Any]]:
        candidates = self._cleanup_candidates(snapshot)
        if not candidates:
            return None
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        overwrite_sources = overwrite_sources or {"scheduled"}
        if pending_plan and pending_plan.get("source") not in overwrite_sources:
            logger.info("媒体库管家已有手动清理批次，跳过本次定时批次覆盖")
            return None
        plan = self._build_cleanup_plan(
            candidates,
            bool(self._config.get("default_delete_source")),
            source=source,
            criteria=self._cleanup_criteria_summary(),
        )
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        if self._config.get("notify_enabled"):
            self._notify_cleanup_batch(plan)
        return plan

    def _cleanup_candidates(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        libraries = self._config.get("cleanup_libraries") or []
        media_items = snapshot.get("media", []) or []
        candidates = []
        for item in media_items:
            if libraries and not self._media_in_cleanup_library(item, libraries):
                continue
            if self._matches_cleanup_conditions(item):
                candidates.append(item)
        return sorted(candidates, key=lambda item: (-(int(item.get("size") or 0)), item.get("last_watched_at") or "", item.get("title") or ""))

    def _media_in_cleanup_library(self, item: Dict[str, Any], libraries: List[str]) -> bool:
        values = {
            self._clean_text(item.get("library")),
            self._clean_text(item.get("library_id")),
            self._clean_text(item.get("library_item_id")),
        }
        filters = {self._clean_text(value) for value in libraries if self._clean_text(value)}
        return bool(values & filters)

    def _matches_cleanup_conditions(self, item: Dict[str, Any]) -> bool:
        rules = self._config.get("cleanup_rules") or []
        return any(self._matches_cleanup_rule(item, rule) for rule in rules)

    def _matches_cleanup_rule(self, item: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        checks = []
        watch_state = rule.get("watch_state")
        if watch_state == "watched":
            checks.append(bool(item.get("watched")))
        elif watch_state == "unwatched":
            checks.append(not bool(item.get("watched")))
        days = int(rule.get("unwatched_days") or 0)
        if days > 0:
            checks.append(self._inactive_days(item) >= days)
        min_size = int(rule.get("min_size_gb") or 0)
        if min_size > 0:
            checks.append(int(item.get("size") or 0) >= min_size * 1024 ** 3)
        max_rating = float(rule.get("max_rating") or 0)
        if max_rating > 0:
            rating = self._to_float(item.get("rating"), 0)
            checks.append(rating > 0 and rating <= max_rating)
        if not checks:
            return False
        return any(checks) if rule.get("operator") == "or" else all(checks)

    def _cleanup_criteria_summary(self) -> Dict[str, Any]:
        return {
            "libraries": self._config.get("cleanup_libraries") or [],
            "rules": self._config.get("cleanup_rules") or [],
        }

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

        if not records and not delete_targets:
            delete_targets.extend(self._targets_from_directory_mapping(media, delete_source))

        status = "ready" if delete_targets else "no_match"
        if records and delete_targets:
            message = "已匹配整理记录，可执行删除。"
        elif delete_targets:
            dest_count = len([target for target in delete_targets if target.get("kind") == "dest"])
            src_count = len([target for target in delete_targets if target.get("kind") == "src"])
            message = f"未匹配整理记录，已按目录映射识别 {dest_count} 个媒体库文件、{src_count} 个源文件，请审核后执行。"
        else:
            message = "未匹配整理记录，也未能通过目录映射定位文件；接入 AI 后可辅助识别源文件。"
        return {
            "media_id": media.get("id"),
            "title": media.get("title"),
            "type": media.get("type"),
            "type_label": media.get("type_label"),
            "watched": bool(media.get("watched")),
            "watch_state": media.get("watch_state"),
            "size": self._sum_target_size(delete_targets) or int(media.get("size") or 0),
            "library": media.get("library"),
            "rating": media.get("rating"),
            "progress": media.get("progress"),
            "last_episode_added_at": media.get("last_episode_added_at"),
            "last_watched_at": media.get("last_watched_at"),
            "matched_transfer_records": [self._transfer_record_summary(record) for record in records],
            "download_tasks": self._download_tasks_from_records(records),
            "delete_targets": self._dedupe_targets(delete_targets),
            "status": status,
            "message": message,
        }

    def _targets_from_directory_mapping(self, media: Dict[str, Any], delete_source: bool) -> List[Dict[str, Any]]:
        mappings = self._directory_mappings()
        if not mappings:
            return []

        storage = StorageChain()
        targets: List[Dict[str, Any]] = []
        for media_path in self._media_file_paths(media):
            mapping = self._match_directory_mapping(media_path, mappings)
            if not mapping:
                continue
            dest_fileitem = self._fileitem_from_storage_path(
                storage,
                self._clean_text(getattr(mapping, "library_storage", "")) or "local",
                media_path,
            )
            if dest_fileitem:
                targets.append(self._target_from_mapping("dest", media_path, dest_fileitem, mapping))

            transfer_type = self._clean_text(getattr(mapping, "transfer_type", "")).lower()
            if not delete_source or transfer_type not in self.LINK_TRANSFER_TYPES:
                continue
            source_path = self._mapped_source_path(media_path, mapping)
            if not source_path:
                continue
            src_fileitem = self._fileitem_from_storage_path(
                storage,
                self._clean_text(getattr(mapping, "storage", "")) or "local",
                source_path,
            )
            if src_fileitem:
                targets.append(self._target_from_mapping("src", source_path, src_fileitem, mapping))
        return self._dedupe_targets(targets)

    def _directory_mappings(self) -> List[Any]:
        try:
            return [
                item
                for item in DirectoryHelper().get_download_dirs()
                if self._clean_text(getattr(item, "download_path", ""))
                and self._clean_text(getattr(item, "library_path", ""))
            ]
        except Exception as err:
            logger.warning(f"媒体库管家读取 MoviePilot 目录映射失败：{err}")
            return []

    def _match_directory_mapping(self, media_path: str, mappings: List[Any]) -> Optional[Any]:
        matches = [
            item
            for item in mappings
            if self._path_is_relative_to(media_path, self._clean_text(getattr(item, "library_path", "")))
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda item: len(self._clean_text(getattr(item, "library_path", ""))), reverse=True)[0]

    def _mapped_source_path(self, media_path: str, mapping: Any) -> str:
        download_path = self._normalized_path_text(getattr(mapping, "download_path", ""))
        relative_path = self._relative_path(media_path, getattr(mapping, "library_path", ""))
        if not download_path or not relative_path:
            return ""
        return f"{download_path}/{relative_path}"

    def _target_from_mapping(self, kind: str, path: str, fileitem: Dict[str, Any], mapping: Any) -> Dict[str, Any]:
        size = self._to_int(fileitem.get("size") or fileitem.get("size_bytes"), 0)
        return {
            "record_id": None,
            "kind": kind,
            "kind_label": "媒体库文件" if kind == "dest" else "源文件",
            "path": path,
            "path_preview": self._path_preview(path),
            "size": size,
            "fileitem": fileitem,
            "match_source": "directory_mapping",
            "directory_mapping": {
                "name": self._clean_text(getattr(mapping, "name", "")),
                "transfer_type": self._clean_text(getattr(mapping, "transfer_type", "")),
                "download_path": self._path_preview(getattr(mapping, "download_path", "")),
                "library_path": self._path_preview(getattr(mapping, "library_path", "")),
            },
        }

    def _fileitem_from_storage_path(self, storage: StorageChain, storage_name: str, path: str) -> Optional[Dict[str, Any]]:
        if not path:
            return None
        try:
            fileitem = storage.get_file_item(storage=storage_name or "local", path=Path(path))
        except Exception as err:
            logger.warning(f"媒体库管家读取文件项失败 {path}: {err}")
            return None
        if not fileitem:
            return None
        if hasattr(fileitem, "model_dump"):
            return fileitem.model_dump()
        if hasattr(fileitem, "dict"):
            return fileitem.dict()
        return dict(fileitem)

    def _media_file_paths(self, media: Dict[str, Any]) -> List[str]:
        if media.get("type") == "series":
            paths = media.get("episode_paths") or []
        else:
            paths = []
        if not paths and media.get("path"):
            paths = [media.get("path")]
        result = []
        for path in paths:
            clean_path = self._clean_text(path)
            if clean_path and clean_path not in result:
                result.append(clean_path)
        return result

    @classmethod
    def _path_is_relative_to(cls, path: Any, root: Any) -> bool:
        clean_path = cls._normalized_path_text(path)
        clean_root = cls._normalized_path_text(root)
        return bool(clean_path and clean_root and (clean_path == clean_root or clean_path.startswith(clean_root + "/")))

    @classmethod
    def _relative_path(cls, path: Any, root: Any) -> str:
        clean_path = cls._normalized_path_text(path)
        clean_root = cls._normalized_path_text(root)
        if not clean_path or not clean_root or clean_path == clean_root:
            return ""
        if clean_path.startswith(clean_root + "/"):
            return clean_path[len(clean_root) + 1 :]
        return ""

    @staticmethod
    def _normalized_path_text(path: Any) -> str:
        return str(path or "").replace("\\", "/").rstrip("/")

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
            "downloader": self._clean_text(getattr(record, "downloader", "")),
            "download_hash": self._clean_text(getattr(record, "download_hash", "")),
            "date": self._clean_text(getattr(record, "date", "")),
        }

    def _download_tasks_from_records(self, records: List[Any]) -> List[Dict[str, Any]]:
        allowed_downloaders = self._selected_downloader_names()
        tasks = []
        for record in records:
            downloader = self._clean_text(getattr(record, "downloader", ""))
            download_hash = self._clean_text(getattr(record, "download_hash", ""))
            if not downloader or not download_hash:
                continue
            if allowed_downloaders and downloader not in allowed_downloaders:
                continue
            service_info = DownloaderHelper().get_service(name=downloader)
            dtype = self._clean_text(getattr(service_info, "type", "")).lower() if service_info else ""
            if dtype not in self.SUPPORTED_DOWNLOADER_TYPES:
                continue
            tasks.append({
                "record_id": getattr(record, "id", None),
                "title": self._clean_text(getattr(record, "title", "")),
                "downloader": downloader,
                "downloader_type": dtype,
                "download_hash": download_hash,
            })
        return self._dedupe_download_tasks(tasks)

    def _selected_downloader_names(self) -> set:
        configured = set(self._config.get("downloaders") or [])
        if configured:
            return configured
        return {option["value"] for option in self._downloader_options() if option.get("value")}

    @staticmethod
    def _dedupe_download_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for task in tasks:
            key = (task.get("downloader"), task.get("download_hash"))
            if not key[0] or not key[1] or key in seen:
                continue
            seen.add(key)
            result.append(task)
        return result

    @staticmethod
    def _path_matches(media_path: str, record_path: str) -> bool:
        left = media_path.replace("\\", "/").rstrip("/").lower()
        right = str(record_path or "").replace("\\", "/").rstrip("/").lower()
        return bool(left and right and (left == right or right.startswith(left + "/") or left.startswith(right + "/")))

    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        executable_items = [item for item in plan.get("items", []) if item.get("status") == "ready"]
        targets = self._dedupe_targets([target for item in executable_items for target in item.get("delete_targets", [])])
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
        deleted_seed_tasks, failed_seed_tasks = self._delete_seed_tasks(plan, record_status)
        for record_id, ok in record_status.items():
            if not ok or record_id is None:
                continue
            try:
                oper.delete(record_id)
                deleted_records += 1
            except Exception as err:
                failed_targets.append({"record_id": record_id, "kind": "record", "path": "", "error": f"整理记录删除失败：{err}"})

        for task in failed_seed_tasks:
            failed_targets.append({
                "record_id": task.get("record_id"),
                "kind": "downloader",
                "path": task.get("download_hash", ""),
                "path_preview": f"{task.get('downloader')} / {task.get('download_hash', '')[:12]}",
                "error": task.get("error") or "下载器任务删除失败",
            })

        reclaim_size = self._sum_target_size(deleted_targets)
        success = not failed_targets
        seed_task_text = f"，保种任务 {len(deleted_seed_tasks)} 个" if self._config.get("delete_seed_tasks") else ""
        return {
            "plan_id": plan.get("id"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success" if success else "failed",
            "delete_source": bool(plan.get("delete_source")),
            "reclaim_size": reclaim_size,
            "deleted_records": deleted_records,
            "deleted_seed_tasks": deleted_seed_tasks,
            "failed_seed_tasks": failed_seed_tasks,
            "deleted_targets": deleted_targets,
            "failed_targets": failed_targets,
            "items": [{"title": item.get("title"), "type": item.get("type"), "size": item.get("size")} for item in executable_items],
            "message": f"清理完成，删除 {len(deleted_targets)} 个文件，整理记录 {deleted_records} 条{seed_task_text}。" if success else f"清理未完全成功，失败 {len(failed_targets)} 项，请查看执行记录。",
        }

    def _delete_seed_tasks(self, plan: Dict[str, Any], record_status: Dict[Any, bool]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self._config.get("delete_seed_tasks"):
            return [], []
        successful_record_ids = {record_id for record_id, ok in record_status.items() if ok and record_id is not None}
        tasks = self._dedupe_download_tasks([
            task
            for item in plan.get("items", [])
            for task in item.get("download_tasks", []) or []
            if task.get("record_id") in successful_record_ids
        ])
        if not tasks:
            return [], []

        helper = DownloaderHelper()
        deleted: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        for task in tasks:
            try:
                downloader = task.get("downloader")
                service_info = helper.get_service(name=downloader)
                dtype = self._clean_text(getattr(service_info, "type", "")).lower() if service_info else ""
                if dtype not in self.SUPPORTED_DOWNLOADER_TYPES:
                    raise RuntimeError("Downloader unavailable or unsupported")
                module = getattr(service_info, "module", None)
                if not module or not hasattr(module, "remove_torrents"):
                    raise RuntimeError("Downloader module cannot remove torrents")
                result = module.remove_torrents(
                    hashs=[task.get("download_hash")],
                    delete_file=False,
                    downloader=downloader,
                )
                if result is not True:
                    raise RuntimeError("Downloader returned failure")
                deleted.append(task)
            except Exception as err:
                failed.append({**task, "error": str(err)})
        return deleted, failed

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

    def _notify_cleanup_batch(self, plan: Dict[str, Any]) -> None:
        items = plan.get("items") or []
        lines = [
            f"批次：{plan.get('batch_id') or plan.get('id')}",
            f"命中媒体：{len(items)} 个，可执行条目：{plan.get('ready_count', 0)} 个",
            f"预计可释放：{self._human_size(plan.get('estimated_reclaim_size'))}",
            "请进入媒体库管家清理计划页增删条目并确认执行。",
        ]
        for item in items[:8]:
            lines.append(f"- {item.get('title')} / {item.get('library') or item.get('type_label')} / {self._human_size(item.get('size'))}")
        if len(items) > 8:
            lines.append(f"... 另有 {len(items) - 8} 个媒体")
        self.post_message(mtype=NotificationType.MediaServer, title="【媒体库管家】清理批次待确认", text="\n".join(lines))

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

    @staticmethod
    def _cache_meta(snapshot: Dict[str, Any]) -> Dict[str, Any]:
        libraries = snapshot.get("libraries") or []
        media = snapshot.get("media") or []
        return {
            "source": "database",
            "has_snapshot": bool(snapshot),
            "scanned_at": snapshot.get("scanned_at"),
            "library_count": len(libraries),
            "media_count": len(media),
        }

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

    def _attach_media_volume_info(self, media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        volume_cache: Dict[Any, Dict[str, Any]] = {}
        for item in media_items:
            volumes = []
            for path in self._media_volume_paths(item):
                volume = self._volume_status_for_path(path, volume_cache)
                if volume and volume.get("key") not in {value.get("key") for value in volumes}:
                    volumes.append(volume)
            item["volumes"] = [{key: value for key, value in volume.items() if key != "key"} for volume in volumes]
            if not volumes:
                item["volume_name"] = ""
                item["volume_free_percent"] = None
                item["volume_summary"] = ""
                continue
            lowest = min(volumes, key=lambda volume: float(volume.get("free_percent") or 0))
            item["volume_name"] = " / ".join(volume.get("display_name") or volume.get("mount_point") or "" for volume in volumes)
            item["volume_free_percent"] = lowest.get("free_percent")
            item["volume_summary"] = " / ".join(
                f"{volume.get('display_name') or volume.get('mount_point')} {volume.get('free_percent')}%"
                for volume in volumes
            )
        return media_items

    def _media_volume_paths(self, item: Dict[str, Any]) -> List[Any]:
        paths = []
        if item.get("type") == "series":
            paths.extend(item.get("episode_paths") or [])
        if item.get("path"):
            paths.append(item.get("path"))
        result = []
        for path in paths:
            clean_path = self._clean_text(path)
            if clean_path and clean_path not in result:
                result.append(clean_path)
        return result

    def _volume_status_for_path(self, path: Any, cache: Dict[Any, Dict[str, Any]]) -> Dict[str, Any]:
        disk_path = self._existing_disk_path(path)
        if not disk_path:
            return {}
        disk = self._disk_identity(disk_path)
        if not disk:
            return {}
        key = disk.get("key")
        if key in cache:
            return cache[key]
        try:
            usage = shutil.disk_usage(disk["path"])
            free_percent = round(usage.free * 100 / usage.total, 2) if usage.total else 0
            warning = usage.free <= self._config["disk_warning_free_gb"] * 1024 ** 3 or free_percent <= self._config["disk_warning_free_percent"]
            cache[key] = {
                "key": key,
                "path": disk["path"],
                "display_name": disk.get("display_name") or disk["path"],
                "mount_point": disk.get("mount_point") or disk["path"],
                "device": disk.get("device") or "",
                "total": usage.total,
                "free": usage.free,
                "free_percent": free_percent,
                "warning": warning,
            }
        except Exception as err:
            cache[key] = {
                "key": key,
                "path": disk["path"],
                "display_name": disk.get("display_name") or disk["path"],
                "mount_point": disk.get("mount_point") or disk["path"],
                "device": disk.get("device") or "",
                "total": 0,
                "free": 0,
                "free_percent": 0,
                "warning": False,
                "error": str(err),
            }
        return cache[key]

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
        if status == "empty":
            return "当前清理批次没有媒体条目，可从媒体库中选择条目加入。"
        if status == "ready":
            return "清理计划已生成，所有条目均匹配到可删除文件。执行前请再次确认删除范围。"
        blocked = len([item for item in items if item.get("status") != "ready"])
        return f"清理计划存在 {blocked} 个未定位到删除文件的条目，已阻止真实删除。"

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
