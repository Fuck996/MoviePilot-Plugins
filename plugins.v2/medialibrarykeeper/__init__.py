from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Body

from app import schemas
from app.api.endpoints.plugin import register_plugin_api
from app.core.event import Event, eventmanager
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType


class MediaLibraryKeeper(_PluginBase):
    """
    媒体库管家。

    第一阶段只提供 Vue 管理页、接口合同和安全的清理计划预览边界。
    真实 Emby 拉取、整理记录匹配和文件删除需要在后续阶段接入 MoviePilot 主链路。
    """

    plugin_name = "媒体库管家"
    plugin_desc = "管理 Emby 媒体库观看进度、空间风险和清理计划。"
    plugin_icon = "emby.png"
    plugin_version = "0.1.0"
    plugin_author = "liuyuexi1987"
    author_url = "https://github.com/liuyuexi1987"
    plugin_config_prefix = "medialibrarykeeper_"
    plugin_order = 48
    auth_level = 1

    DATA_KEY_HISTORY = "history"
    DATA_KEY_PENDING_PLAN = "pending_plan"

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
        return (
            {"cols": 12, "sm": 6, "md": 4},
            {
                "title": "媒体库管家",
                "subtitle": "空间风险与清理建议",
                "refresh": 60,
                "border": True,
            },
            None,
        )

    def stop_service(self):
        pass

    def get_status(self) -> schemas.Response:
        return schemas.Response(
            success=True,
            data={
                "config": self._config,
                "summary": self._build_summary(),
                "media": [],
                "recommendations": [],
                "pending_plan": self.get_data(self.DATA_KEY_PENDING_PLAN) or None,
                "history": self._load_history(),
                "capabilities": self._capabilities(),
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
            logger.error(f"保存媒体库管家配置失败: {err}")
            return schemas.Response(success=False, message=str(err))

    def scan_library_api(self) -> schemas.Response:
        return schemas.Response(
            success=False,
            message="Emby 媒体库拉取链路尚未接入。下一阶段需要复用 MoviePilot 已配置的媒体服务器连接。",
            data=self.get_status().data,
        )

    def create_cleanup_plan_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        selected_items = payload.get("items") or []
        if not selected_items:
            return schemas.Response(success=False, message="请先选择要清理的媒体条目")

        plan_items = []
        for item in selected_items:
            plan_items.append(
                {
                    "media_id": self._clean_text(item.get("id")),
                    "title": self._clean_text(item.get("title")),
                    "type": self._clean_text(item.get("type")),
                    "season": item.get("season"),
                    "watched": bool(item.get("watched")),
                    "size": int(item.get("size") or 0),
                    "matched_transfer_records": [],
                    "delete_targets": [],
                    "status": "waiting_match",
                    "message": "尚未接入整理记录匹配，当前仅生成预览占位。",
                }
            )

        plan = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": self._clean_text(payload.get("mode")) or "preview",
            "delete_source": bool(payload.get("delete_source", self._config.get("default_delete_source"))),
            "items": plan_items,
            "estimated_reclaim_size": sum(item.get("size", 0) for item in plan_items),
            "status": "preview_only",
            "message": "清理计划已生成，但真实文件和整理记录删除尚未接入。",
        }
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        return schemas.Response(success=True, data={"plan": plan, "status": self.get_status().data})

    def execute_cleanup_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        payload = payload or {}
        plan_id = self._clean_text(payload.get("plan_id"))
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        if not plan_id or pending_plan.get("id") != plan_id:
            return schemas.Response(success=False, message="清理计划不存在或已失效")
        return schemas.Response(
            success=False,
            message="真实删除链路尚未接入，已阻止执行。后续需要先接入 TransferHistoryOper 与 StorageChain。",
            data={"plan": pending_plan},
        )

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
            "library_names": [],
        }

    @classmethod
    def _normalize_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        defaults = cls._default_config()
        normalized = {**defaults, **(config or {})}
        normalized["enabled"] = bool(normalized.get("enabled"))
        normalized["show_sidebar_nav"] = bool(normalized.get("show_sidebar_nav", True))
        normalized["notify_enabled"] = bool(normalized.get("notify_enabled", True))
        normalized["disk_warning_enabled"] = bool(normalized.get("disk_warning_enabled", True))
        normalized["ai_suggestions"] = bool(normalized.get("ai_suggestions", False))
        normalized["default_delete_source"] = bool(normalized.get("default_delete_source", False))
        normalized["disk_warning_free_gb"] = max(cls._to_int(normalized.get("disk_warning_free_gb"), 200), 0)
        normalized["disk_warning_free_percent"] = max(cls._to_int(normalized.get("disk_warning_free_percent"), 10), 0)
        normalized["scan_cron"] = cls._clean_text(normalized.get("scan_cron")) or defaults["scan_cron"]
        library_names = normalized.get("library_names")
        if isinstance(library_names, str):
            library_names = [line.strip() for line in library_names.splitlines() if line.strip()]
        normalized["library_names"] = library_names if isinstance(library_names, list) else []
        return normalized

    @staticmethod
    def _to_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clean_text(value: Any) -> str:
        return str(value or "").strip()

    def _load_history(self) -> List[Dict[str, Any]]:
        history = self.get_data(self.DATA_KEY_HISTORY) or []
        return history if isinstance(history, list) else []

    def _build_summary(self) -> Dict[str, Any]:
        return {
            "libraries": 0,
            "movies": 0,
            "series": 0,
            "episodes": 0,
            "watched_series": 0,
            "unwatched_large_series": 0,
            "estimated_reclaim_size": 0,
            "disk_warning": False,
            "last_scan_at": None,
            "connection_state": "not_connected",
        }

    @staticmethod
    def _capabilities() -> Dict[str, Any]:
        return {
            "emby_scan": False,
            "transfer_history_match": False,
            "storage_delete": False,
            "ai_suggestions": False,
            "notification": False,
        }

    @eventmanager.register(EventType.PluginReload)
    def reload(self, event: Event):
        if event and event.event_data and event.event_data.get("plugin_id") == self.__class__.__name__:
            register_plugin_api(plugin_id=self.__class__.__name__)
