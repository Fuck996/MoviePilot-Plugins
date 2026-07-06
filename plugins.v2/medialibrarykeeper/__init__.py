import asyncio
import json
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

from apscheduler.triggers.cron import CronTrigger
from fastapi import Body, Depends, HTTPException, Response, status

from app import schemas
from app.chain.storage import StorageChain
from app.core.config import settings
from app.core.event import eventmanager, Event
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
    from app.db.downloadhistory_oper import DownloadHistoryOper
except Exception:
    DownloadHistoryOper = None

try:
    from app.db.models.transferhistory import TransferHistory
except Exception:
    TransferHistory = None


_ACTIVE_PLUGIN = None


def get_medialibrarykeeper_plugin():
    return _ACTIVE_PLUGIN


class MediaLibraryKeeper(_PluginBase):
    """
    媒体库管家。
    通过 MoviePilot 已配置的媒体服务器读取 Emby 媒体库，并复用整理记录与 StorageChain 执行清理。
    """

    plugin_name = "媒体库管家"
    plugin_desc = "自动定期整理Emby媒体库资源，联合清理释放硬盘空间。"
    plugin_icon = "emby.png"
    plugin_version = "1.0.17"
    plugin_author = "fuck996"
    author_url = "https://github.com/Fuck996"
    plugin_config_prefix = "medialibrarykeeper_"
    plugin_order = 48
    auth_level = 1
    MESSAGE_ACTION_CONFIRM_CLEANUP = "cleanup_confirm:"

    DATA_KEY_HISTORY = "history"
    DATA_KEY_PENDING_PLAN = "pending_plan"
    DATA_KEY_CLEANUP_QUEUE = "cleanup_queue"
    DATA_KEY_SNAPSHOT = "snapshot"
    DATA_KEY_LAST_DISK_WARNING = "last_disk_warning"
    SUPPORTED_DOWNLOADER_TYPES = {"qbittorrent", "transmission"}
    LINK_TRANSFER_TYPES = {"link", "softlink"}
    MEDIA_FILE_EXTENSIONS = {".avi", ".flv", ".m2ts", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".rmvb", ".ts", ".wmv"}
    SCRAPING_FILE_EXTENSIONS = {".ass", ".jpg", ".jpeg", ".nfo", ".png", ".srt", ".ssa", ".sup", ".webp"}

    def __init__(self):
        super().__init__()
        self._config: Dict[str, Any] = self._default_config()
        self._enabled = False
        self._queue_lock = threading.Lock()
        self._queue_worker: Optional[threading.Thread] = None

    def init_plugin(self, config: dict = None):
        global _ACTIVE_PLUGIN
        _ACTIVE_PLUGIN = self
        config = self._normalize_config(config or {})
        self._config = config
        self._enabled = bool(config.get("enabled"))
        self._resume_cleanup_queue()

    def get_state(self) -> bool:
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_agent_tools(self) -> List[type]:
        try:
            from .agenttool import MediaLibraryKeeperSeedReviewTool
        except Exception as err:
            logger.warning(f"媒体库管家 AI 智能体工具注册失败：{err}")
            return []
        return [MediaLibraryKeeperSeedReviewTool]

    def get_service(self) -> Optional[List[Dict[str, Any]]]:
        if not self._enabled or not self._config.get("scan_cron"):
            return None
        try:
            trigger = CronTrigger.from_crontab(
                self._config["scan_cron"], timezone=settings.TZ
            )
        except Exception as err:
            logger.error(f"媒体库管家定时扫描 Cron 配置无效：{err}")
            return None
        return [
            {
                "id": "MediaLibraryKeeperScan",
                "name": "媒体库管家定时扫描",
                "trigger": trigger,
                "func": self.scan_library,
                "func_kwargs": {"notify_disk_warning": True, "build_cleanup_batch": True},
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
                "path": "/libraries/sync",
                "endpoint": self.sync_libraries_api,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "同步媒体库列表",
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
        if not self._config.get("show_sidebar_nav", True):
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
                "cleanup_queue": self._queue_status(),
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
            self._refresh_scheduled_service()
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

    def sync_libraries_api(self, payload: Dict[str, Any] = Body(default=None)) -> schemas.Response:
        try:
            payload = payload or {}
            mediaservers = [
                self._clean_text(item)
                for item in payload.get("mediaservers") or []
                if self._clean_text(item)
            ]
            libraries = self.sync_libraries(name_filters=mediaservers if "mediaservers" in payload else None)
            status_data = self.get_status().data
            return schemas.Response(
                success=True,
                message=f"媒体库列表已同步，共 {len(libraries)} 个媒体库",
                data=status_data,
            )
        except Exception as err:
            logger.error(f"媒体库管家同步媒体库列表失败：{err}")
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
                logger.info(
                    "媒体库管家手动检查未发送清理批次通知："
                    f"已有不可覆盖批次 batch={pending_plan.get('batch_id') or pending_plan.get('id')}，"
                    f"source={pending_plan.get('source')}"
                )
                return schemas.Response(success=True, message="当前已有手动清理批次，已保留原批次未覆盖", data=status_data)
            logger.info("媒体库管家手动检查未发送清理批次通知：当前清理规则未命中媒体")
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
        watch_audit: List[Dict[str, Any]] = []
        errors: List[str] = []
        for server_name, service_info in services.items():
            service = service_info.instance
            try:
                scan_users = self._resolve_emby_scan_users(service, service_info)
                if not scan_users:
                    errors.append(f"{server_name} 未解析到 Emby 用户，请检查 MoviePilot 媒体服务器用户名配置。")
                    continue
                user_id = scan_users[0]["id"]
                server_libraries = self._fetch_emby_libraries(service, service_info, server_name, user_id)
                libraries.extend(server_libraries)
                for library in server_libraries:
                    library_media, library_audit = self._fetch_emby_items(service, service_info, server_name, scan_users, library)
                    media.extend(library_media)
                    if library_audit:
                        watch_audit.append(library_audit)
            except Exception as err:
                logger.error(f"媒体库管家读取 Emby {server_name} 失败：{err}")
                errors.append(f"{server_name}: {err}")

        media_items = self._attach_media_volume_info(self._dedupe_media(media))
        watch_audit_result = self._build_watch_audit(watch_audit, media_items)
        self._log_watch_audit(watch_audit_result)
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

    def _refresh_scheduled_service(self) -> None:
        from app.scheduler import Scheduler

        Scheduler().update_plugin_job(self.__class__.__name__)
        logger.info(
            "媒体库管家定时扫描服务已刷新："
            f"enabled={self._enabled}，scan_cron={self._config.get('scan_cron')}"
        )

    def sync_libraries(self, name_filters: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        services = self._active_emby_services(name_filters=name_filters)
        if not services:
            raise RuntimeError("没有可用的 Emby 媒体服务器，请先在 MoviePilot 媒体服务器中完成配置。")

        libraries: List[Dict[str, Any]] = []
        errors: List[str] = []
        for server_name, service_info in services.items():
            service = service_info.instance
            try:
                scan_users = self._resolve_emby_scan_users(service, service_info)
                if not scan_users:
                    errors.append(f"{server_name} 未解析到 Emby 用户，请检查 MoviePilot 媒体服务器用户名配置。")
                    continue
                libraries.extend(self._fetch_emby_libraries(service, service_info, server_name, scan_users[0]["id"]))
            except Exception as err:
                logger.error(f"媒体库管家读取 Emby {server_name} 媒体库列表失败：{err}")
                errors.append(f"{server_name}: {err}")

        deduped_libraries = self._dedupe_libraries(libraries)
        snapshot = self._load_snapshot()
        snapshot.update({
            "libraries": deduped_libraries,
            "library_synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "library_sync_errors": errors,
        })
        self.save_data(self.DATA_KEY_SNAPSHOT, snapshot)
        logger.info(f"媒体库管家媒体库列表同步完成：libraries={len(deduped_libraries)}，errors={len(errors)}")
        return deduped_libraries

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

        delete_source = bool(self._config.get("default_delete_source"))
        plan = self._build_cleanup_plan([media_index[item_id] for item_id in selected_ids], delete_source, source="manual")
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        if self._config.get("notify_enabled"):
            logger.info(
                "媒体库管家手动整理生成清理批次，准备发送通知："
                f"batch={plan.get('batch_id') or plan.get('id')}，items={len(plan.get('items') or [])}，"
                f"ready={plan.get('ready_count', 0)}"
            )
            self._notify_cleanup_batch(plan)
        else:
            logger.info(
                "媒体库管家手动整理生成清理批次但通知跳过："
                f"batch={plan.get('batch_id') or plan.get('id')}，notify_enabled=False"
            )
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

        plan_items = list(pending_plan.get("items") or [])
        current_ids = [item.get("media_id") for item in plan_items if item.get("media_id")]
        changed_items: List[Dict[str, Any]] = []
        requested_count = len(item_ids)
        if action == "remove":
            remove_ids = set(item_ids)
            next_items = [item for item in plan_items if item.get("media_id") not in remove_ids]
            changed_items = [item for item in plan_items if item.get("media_id") in remove_ids]
            plan = {**pending_plan, "items": next_items}
            added_count = 0
            removed_count = len(changed_items)
        else:
            snapshot = self._load_snapshot()
            media_index = {item.get("id"): item for item in snapshot.get("media", [])}
            existing_ids = set(current_ids)
            new_ids = [item_id for item_id in dict.fromkeys(item_ids) if item_id not in existing_ids]
            missing = [item_id for item_id in new_ids if item_id not in media_index]
            if missing:
                return schemas.Response(success=False, message="所选媒体不在最近一次扫描结果中，请先重新扫描媒体库。")
            changed_items = [self._build_plan_item(media_index[item_id], bool(pending_plan.get("delete_source"))) for item_id in new_ids]
            plan = {**pending_plan, "items": [*plan_items, *changed_items]}
            added_count = len(changed_items)
            removed_count = 0

        self._refresh_cleanup_plan(plan)
        self.save_data(self.DATA_KEY_PENDING_PLAN, plan)
        logger.info(
            "媒体库管家清理计划更新："
            f"batch={plan.get('batch_id') or plan.get('id')}，action={action}，"
            f"requested={requested_count}，added={added_count}，removed={removed_count}，"
            f"items={len(plan.get('items') or [])}，ready={plan.get('ready_count', 0)}，"
            f"estimated={self._human_size(plan.get('estimated_reclaim_size'))}，"
            f"delete_source={bool(plan.get('delete_source'))}"
        )
        for item in changed_items:
            self._log_cleanup_plan_item(plan, item, "媒体库管家清理计划更新识别")
        message = "已移出清理批次" if action == "remove" else "已加入清理批次" if added_count else "所选媒体已在当前批次中"
        return schemas.Response(success=True, message=message, data={"plan": plan, "status": self.get_status().data})

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
        success, message = self._confirm_cleanup_plan(plan_id)
        return schemas.Response(success=success, message=message, data=self.get_status().data)

    @eventmanager.register(EventType.MessageAction)
    def message_action(self, event: Event):
        event_data = event.event_data or {}
        if event_data.get("plugin_id") != self.__class__.__name__:
            return
        text = self._clean_text(event_data.get("text"))
        if not text.startswith(self.MESSAGE_ACTION_CONFIRM_CLEANUP):
            return

        plan_id = self._clean_text(text.replace(self.MESSAGE_ACTION_CONFIRM_CLEANUP, "", 1))
        success, message = self._confirm_cleanup_plan(plan_id)
        title = "【媒体库管家】已确认清理批次" if success else "【媒体库管家】清理批次确认失败"
        link = self._cleanup_page_url()
        message_kwargs = {
            "channel": event_data.get("channel"),
            "title": title,
            "text": message,
            "userid": event_data.get("userid") or event_data.get("user"),
            "buttons": self._cleanup_message_buttons(self._cleanup_page_buttons()) or None,
            "original_message_id": event_data.get("original_message_id"),
            "original_chat_id": event_data.get("original_chat_id"),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        if link:
            message_kwargs["link"] = link
        self.post_message(**message_kwargs)

    def get_history_api(self) -> schemas.Response:
        return schemas.Response(success=True, data={"history": self._load_history()})

    def _confirm_cleanup_plan(self, plan_id: str) -> Tuple[bool, str]:
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        clean_plan_id = self._clean_text(plan_id)
        if not clean_plan_id or pending_plan.get("id") != clean_plan_id:
            return False, "清理计划不存在或已失效。"
        if self._plan_ready_count(pending_plan) <= 0:
            return False, pending_plan.get("message") or "清理计划没有可执行条目。"

        queue_item = self._enqueue_cleanup_plan(pending_plan)
        self.save_data(self.DATA_KEY_PENDING_PLAN, None)
        self._ensure_cleanup_worker()
        return True, (
            f"已确认批次 {pending_plan.get('batch_id') or pending_plan.get('id')}，"
            f"加入清理队列 {queue_item.get('id')}；后台执行完成后会写入执行记录。"
        )

    def _enqueue_cleanup_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        with self._queue_lock:
            queue = self._load_cleanup_queue()
            for item in queue:
                if item.get("plan_id") == plan.get("id") and item.get("status") in {"queued", "running"}:
                    return item
            now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            queue_item = {
                "id": f"{plan.get('id')}-{datetime.now().strftime('%H%M%S%f')}",
                "plan_id": plan.get("id"),
                "batch_id": plan.get("batch_id") or plan.get("id"),
                "created_at": now_text,
                "started_at": "",
                "status": "queued",
                "message": "等待执行",
                "item_count": len(plan.get("items") or []),
                "ready_count": self._plan_ready_count(plan),
                "estimated_reclaim_size": plan.get("estimated_reclaim_size") or 0,
                "delete_source": bool(plan.get("delete_source")),
                "plan": plan,
            }
            queue.append(queue_item)
            self.save_data(self.DATA_KEY_CLEANUP_QUEUE, queue[:20])
            return queue_item

    def _resume_cleanup_queue(self) -> None:
        with self._queue_lock:
            queue = self._load_cleanup_queue()
            changed = False
            for item in queue:
                if item.get("status") == "running":
                    item["status"] = "queued"
                    item["message"] = "插件重载后等待重新执行"
                    item["started_at"] = ""
                    changed = True
            if changed:
                self.save_data(self.DATA_KEY_CLEANUP_QUEUE, queue)
        self._ensure_cleanup_worker()

    def _ensure_cleanup_worker(self) -> None:
        with self._queue_lock:
            if self._queue_worker and self._queue_worker.is_alive():
                return
            if not any(item.get("status") in {"queued", "running"} for item in self._load_cleanup_queue()):
                return
            self._queue_worker = threading.Thread(target=self._run_cleanup_queue, name="MediaLibraryKeeperCleanupQueue", daemon=True)
            self._queue_worker.start()

    def _run_cleanup_queue(self) -> None:
        while True:
            queue_item = self._take_next_cleanup_queue_item()
            if not queue_item:
                return
            result = self._run_cleanup_queue_item(queue_item)
            self._complete_cleanup_queue_item(queue_item, result)

    def _take_next_cleanup_queue_item(self) -> Optional[Dict[str, Any]]:
        with self._queue_lock:
            queue = self._load_cleanup_queue()
            for item in queue:
                if item.get("status") not in {"queued", "running"}:
                    continue
                if item.get("status") == "queued":
                    item["status"] = "running"
                    item["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    item["message"] = "正在执行"
                    self.save_data(self.DATA_KEY_CLEANUP_QUEUE, queue)
                return dict(item)
        return None

    def _run_cleanup_queue_item(self, queue_item: Dict[str, Any]) -> Dict[str, Any]:
        plan = queue_item.get("plan") or {}
        try:
            result = self._execute_plan(plan)
        except Exception as err:
            logger.error(f"媒体库管家清理队列执行失败：{err}")
            result = {
                "plan_id": plan.get("id") or queue_item.get("plan_id"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "failed",
                "delete_source": bool(plan.get("delete_source")),
                "reclaim_size": 0,
                "deleted_records": 0,
                "deleted_media_files": 0,
                "deleted_scraping_files": 0,
                "deleted_source_files": 0,
                "deleted_seed_tasks": [],
                "failed_seed_tasks": [],
                "deleted_targets": [],
                "failed_targets": [{"kind": "queue", "path": "", "path_preview": queue_item.get("batch_id"), "error": str(err)}],
                "items": [{"title": item.get("title"), "type": item.get("type"), "size": item.get("size")} for item in plan.get("items", [])],
                "message": f"清理队列执行失败：{err}",
            }
        result["queue_id"] = queue_item.get("id")
        result["queued_at"] = queue_item.get("created_at")
        result["started_at"] = queue_item.get("started_at")
        return result

    def _complete_cleanup_queue_item(self, queue_item: Dict[str, Any], result: Dict[str, Any]) -> None:
        with self._queue_lock:
            queue = [item for item in self._load_cleanup_queue() if item.get("id") != queue_item.get("id")]
            self.save_data(self.DATA_KEY_CLEANUP_QUEUE, queue)
            history = self._load_history()
            history.insert(0, result)
            self.save_data(self.DATA_KEY_HISTORY, history[:50])
            self._prune_snapshot_after_cleanup(result)
        if self._config.get("notify_enabled"):
            self._notify_cleanup_result(result)

    def _prune_snapshot_after_cleanup(self, result: Dict[str, Any]) -> None:
        removed_media_ids = self._cleanup_removed_media_ids(result)
        deleted_targets = result.get("deleted_targets") or []
        if not removed_media_ids and not deleted_targets:
            return
        snapshot = self._load_snapshot()
        media_items = snapshot.get("media")
        if not isinstance(media_items, list):
            return
        next_media = [item for item in media_items if item.get("id") not in removed_media_ids]
        changed = len(next_media) != len(media_items)
        if deleted_targets:
            next_media = self._attach_media_volume_info([dict(item) for item in next_media])
            changed = True
        if not changed:
            return
        patched = dict(snapshot)
        patched["media"] = next_media
        self.save_data(self.DATA_KEY_SNAPSHOT, patched)
        logger.info(
            "媒体库管家清理缓存刷新："
            f"已从扫描快照移除 {len(media_items) - len(next_media)} 个已清理媒体，"
            f"已按本次清理结果刷新 {len(next_media)} 个剩余媒体的卷容量信息"
        )

    @staticmethod
    def _cleanup_removed_media_ids(result: Dict[str, Any]) -> set:
        failed_media_ids = {
            target.get("media_id")
            for target in result.get("failed_targets", []) or []
            if target.get("kind") == "dest" and target.get("media_id")
        }
        return {
            target.get("media_id")
            for target in result.get("deleted_targets", []) or []
            if target.get("kind") == "dest" and target.get("media_id") and target.get("media_id") not in failed_media_ids
        }

    def _queue_status(self) -> List[Dict[str, Any]]:
        queue = self._load_cleanup_queue()
        rows: List[Dict[str, Any]] = []
        for queue_item in queue:
            if queue_item.get("status") not in {"queued", "running"}:
                continue
            plan = queue_item.get("plan") or {}
            for index, media in enumerate(plan.get("items") or []):
                if media.get("status") != "ready":
                    continue
                rows.append(self._queue_media_status(queue_item, media, index))
        return rows

    def _queue_media_status(self, queue_item: Dict[str, Any], media: Dict[str, Any], index: int) -> Dict[str, Any]:
        status = queue_item.get("status")
        message = queue_item.get("message")
        delete_targets = media.get("delete_targets") or []
        return {
            "id": f"{queue_item.get('id')}-{media.get('media_id') or index}",
            "queue_id": queue_item.get("id"),
            "plan_id": queue_item.get("plan_id"),
            "batch_id": queue_item.get("batch_id"),
            "media_id": media.get("media_id"),
            "title": media.get("title"),
            "type": media.get("type"),
            "type_label": media.get("type_label"),
            "created_at": queue_item.get("created_at"),
            "started_at": queue_item.get("started_at"),
            "status": status,
            "message": message,
            "directory": media.get("volume_name") or media.get("volume_summary") or "",
            "file_count": len(delete_targets),
            "estimated_reclaim_size": self._sum_target_size(delete_targets) or int(media.get("size") or 0),
            "delete_source": bool(queue_item.get("delete_source")),
        }

    def get_seed_review_context(self, limit: int = 20) -> Dict[str, Any]:
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        if not pending_plan:
            return {"plan_id": "", "candidate_count": 0, "candidates": []}
        candidates: List[Dict[str, Any]] = []
        for item in pending_plan.get("items", []) or []:
            for candidate in item.get("seed_candidates", []) or []:
                candidates.append({
                    "plan_id": pending_plan.get("id"),
                    "media_id": item.get("media_id"),
                    "title": item.get("title"),
                    "type_label": item.get("type_label"),
                    "downloader": candidate.get("downloader"),
                    "source_path": candidate.get("source_path"),
                    "downloader_path": candidate.get("downloader_path"),
                    "reason": candidate.get("reason"),
                    "status": candidate.get("status"),
                })
                if len(candidates) >= max(1, int(limit or 20)):
                    return {
                        "plan_id": pending_plan.get("id") or "",
                        "candidate_count": len(candidates),
                        "candidates": candidates,
                    }
        return {
            "plan_id": pending_plan.get("id") or "",
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

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
            "path_mappings": [],
            "downloader_path_mappings": [],
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
        normalized["scan_cron"] = cls._normalize_scan_cron(
            cls._clean_text(normalized.get("scan_cron")) or defaults["scan_cron"]
        )
        for key in ["mediaservers", "downloaders", "cleanup_libraries"]:
            normalized[key] = cls._to_list(normalized.get(key))
        normalized["path_mappings"] = cls._normalize_path_mappings(normalized.get("path_mappings"))
        normalized["downloader_path_mappings"] = cls._normalize_downloader_path_mappings(normalized.get("downloader_path_mappings"))
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
    def _normalize_scan_cron(scan_cron: str) -> str:
        if scan_cron == "0 3 * * 1":
            return "0 3 * * mon"
        return scan_cron

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
    def _normalize_path_mappings(cls, mappings: Any) -> List[Dict[str, str]]:
        if not isinstance(mappings, list):
            return []
        normalized = []
        for mapping in mappings:
            if not isinstance(mapping, dict):
                continue
            emby_path = cls._normalized_path_text(mapping.get("emby_path"))
            mp_path = cls._normalized_path_text(mapping.get("mp_path"))
            if not emby_path or not mp_path:
                continue
            normalized.append({"emby_path": emby_path, "mp_path": mp_path})
        return sorted(normalized, key=lambda item: len(item["emby_path"]), reverse=True)

    @classmethod
    def _normalize_downloader_path_mappings(cls, mappings: Any) -> List[Dict[str, str]]:
        if not isinstance(mappings, list):
            return []
        normalized = []
        for mapping in mappings:
            if not isinstance(mapping, dict):
                continue
            downloader = cls._clean_text(mapping.get("downloader"))
            downloader_path = cls._normalized_path_text(mapping.get("downloader_path"))
            resource_path = cls._normalized_path_text(mapping.get("resource_path"))
            if not downloader or not downloader_path or not resource_path:
                continue
            normalized.append({
                "downloader": downloader,
                "downloader_path": downloader_path,
                "resource_path": resource_path,
            })
        return sorted(normalized, key=lambda item: len(item["resource_path"]), reverse=True)

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
        return cls._to_bool(user_data.get("Played"))

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

    def _active_emby_services(self, name_filters: Optional[List[str]] = None) -> Dict[str, Any]:
        name_filters = name_filters if name_filters is not None else (self._config.get("mediaservers") or None)
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

    def _resolve_emby_scan_users(self, service: Any, service_info: Any) -> List[Dict[str, str]]:
        users = self._fetch_emby_users(service)
        username = self._clean_text(getattr(service, "_username", ""))
        config = getattr(service_info, "config", None)
        config_data = getattr(config, "config", {}) or {}
        username = username or self._clean_text(config_data.get("username"))
        if username:
            for user in users:
                if self._clean_text(user.get("Name")) == username:
                    return [{"id": self._clean_text(user.get("Id")), "name": self._clean_text(user.get("Name"))}]
        scan_users = []
        for user in users:
            user_id = self._clean_text(user.get("Id"))
            if not user_id or (user.get("Policy") or {}).get("IsDisabled"):
                continue
            scan_users.append({"id": user_id, "name": self._clean_text(user.get("Name"))})
        if scan_users:
            return scan_users
        user_id = self._clean_text(getattr(service, "user", ""))
        return [{"id": user_id, "name": ""}] if user_id else []

    def _fetch_emby_libraries(self, service: Any, service_info: Any, server_name: str, user_id: str) -> List[Dict[str, Any]]:
        response = service.get_data(f"[HOST]emby/Users/{user_id}/Views?api_key=[APIKEY]")
        data = response.json() if hasattr(response, "json") else response
        raw_items = data.get("Items") if isinstance(data, dict) else []
        library_paths = self._fetch_emby_library_paths(service)
        libraries = []
        for item in raw_items:
            library = self._normalize_emby_library(item, service_info, server_name)
            if library and self._accept_library_name(library.get("title")):
                emby_paths = library_paths.get(library.get("item_id")) or []
                paths = [self._map_emby_path(path) for path in emby_paths]
                fallback_path = self._map_emby_path(item.get("Path"))
                library["emby_paths"] = emby_paths
                library["paths"] = paths
                library["path"] = paths[0] if paths else fallback_path
                libraries.append(library)
        return libraries

    def _fetch_emby_library_paths(self, service: Any) -> Dict[str, List[str]]:
        response = service.get_data("[HOST]emby/Library/VirtualFolders/Query?api_key=[APIKEY]")
        data = response.json() if hasattr(response, "json") else response
        items = data.get("Items") if isinstance(data, dict) else []
        paths_by_id: Dict[str, List[str]] = {}
        for item in items or []:
            item_id = self._clean_text(item.get("ItemId"))
            if not item_id:
                continue
            paths = []
            for path_info in (item.get("LibraryOptions") or {}).get("PathInfos") or []:
                path = self._clean_text(path_info.get("NetworkPath")) or self._clean_text(path_info.get("Path"))
                if path and path not in paths:
                    paths.append(path)
            paths_by_id[item_id] = paths
        return paths_by_id

    def _fetch_emby_items(
        self,
        service: Any,
        service_info: Any,
        server_name: str,
        scan_users: List[Dict[str, str]],
        library: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        library_item_id = self._clean_text(library.get("item_id"))
        if not library_item_id:
            return [], {}
        user_ids = [user["id"] for user in scan_users if user.get("id")]
        user_id = user_ids[0] if user_ids else ""
        if not user_id:
            return [], {}
        items: List[Dict[str, Any]] = []
        start = 0
        limit = 200
        include_types = self._library_include_types(library.get("type"))
        played_item_ids = set()
        played_episode_ids = set()
        user_data_by_item: Dict[str, Dict[str, Any]] = {}
        episode_user_data_by_item: Dict[str, Dict[str, Any]] = {}
        for scan_user_id in user_ids:
            played_item_ids.update(self._fetch_emby_item_ids(service, scan_user_id, library_item_id, include_types, "IsPlayed=true"))
            played_episode_ids.update(self._fetch_emby_item_ids(service, scan_user_id, library_item_id, "Episode", "IsPlayed=true"))
            self._merge_emby_user_data_map(
                user_data_by_item,
                self._fetch_emby_user_data_by_item(service, scan_user_id, library_item_id, include_types),
            )
            self._merge_emby_user_data_map(
                episode_user_data_by_item,
                self._fetch_emby_user_data_by_item(service, scan_user_id, library_item_id, "Episode"),
            )
        played_media_ids = set()
        played_episode_count = 0
        detail_user_data_count = 0
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
                f"&EnableUserData=true&GroupItems=false"
                f"&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            for item in raw_items:
                item_id = self._clean_text(item.get("Id"))
                merged_user_data = user_data_by_item.get(item_id)
                if merged_user_data:
                    item = {**item, "UserData": merged_user_data}
                if self._needs_emby_user_data_detail(item):
                    detail_user_data = self._fetch_merged_emby_item_detail_user_data(service, user_ids, item_id)
                    if detail_user_data:
                        item = {**item, "UserData": detail_user_data}
                        detail_user_data_count += 1
                normalized = self._normalize_emby_item(
                    item,
                    service_info,
                    server_name,
                    library,
                )
                if not normalized:
                    continue
                if normalized.get("type") == "series":
                    stats = self._fetch_series_episode_stats(
                        service,
                        user_ids,
                        normalized.get("item_id"),
                        played_episode_ids,
                        episode_user_data_by_item,
                    )
                    if stats:
                        normalized["total_episodes"] = stats["total_episodes"] or normalized.get("total_episodes", 0)
                        normalized["watched_episodes"] = stats["watched_episodes"]
                        normalized["size"] = stats["size"] or normalized.get("size", 0)
                        normalized["episode_paths"] = stats["paths"]
                        normalized["last_episode_added_at"] = stats.get("last_episode_added_at") or normalized.get("last_episode_added_at", "")
                        normalized["last_watched_at"] = stats.get("last_watched_at") or normalized.get("last_watched_at", "")
                        played_episode_count += stats["watched_episodes"]
                        detail_user_data_count += stats.get("detail_user_data_count", 0)
                        normalized["watched"] = (
                            normalized["total_episodes"] > 0
                            and normalized["watched_episodes"] >= normalized["total_episodes"]
                        )
                        normalized["watch_state"] = self._watch_state(normalized["watched"])
                        normalized["progress"] = self._progress_text(
                            normalized["watched_episodes"],
                            normalized["total_episodes"],
                            True,
                            normalized["watched"],
                        )
                if self._accept_library(normalized):
                    if normalized.get("watched"):
                        played_media_ids.add(normalized.get("item_id"))
                    items.append(normalized)
            if len(raw_items) < limit:
                break
            start += limit
        audit = {
            "server": server_name,
            "library_id": library.get("id") or "",
            "library_item_id": library_item_id,
            "library": library.get("title") or "",
            "type": library.get("type") or "",
            "include_types": include_types,
            "users": [user.get("name") or user.get("id") for user in scan_users],
            "emby_played_ids": sorted(played_media_ids),
            "played_source": "UserData.Played",
            "played_source_counts": {
                "IsPlayed=true": len(played_item_ids),
                "UserData.Played": len(played_media_ids),
                "detail.UserData": detail_user_data_count,
            },
            "emby_played_episode_count": played_episode_count,
            "played_episode_source_counts": {
                "IsPlayed=true": len(played_episode_ids),
                "UserData.Played": played_episode_count,
            },
            "query": {
                "played": "IsPlayed=true",
            },
        }
        return items, audit

    def _fetch_emby_user_data_by_item(
        self,
        service: Any,
        user_id: str,
        parent_id: str,
        include_types: str,
    ) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        if not user_id or not parent_id or not include_types:
            return result
        start = 0
        limit = 500
        fields = quote("UserData,UserDataPlayCount,UserDataLastPlayedDate")
        while True:
            url = (
                f"[HOST]emby/Users/{user_id}/Items?ParentId={quote(parent_id)}&Recursive=true"
                f"&IncludeItemTypes={include_types}&Fields={fields}&EnableUserData=true"
                f"&GroupItems=false&EnableTotalRecordCount=false"
                f"&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            for item in raw_items:
                item_id = self._clean_text(item.get("Id"))
                user_data = item.get("UserData")
                if item_id and isinstance(user_data, dict):
                    result[item_id] = user_data
            if len(raw_items) < limit:
                break
            start += limit
        return result

    def _merge_emby_user_data_map(self, target: Dict[str, Dict[str, Any]], source: Dict[str, Dict[str, Any]]) -> None:
        for item_id, user_data in source.items():
            target[item_id] = self._merge_emby_user_data(target.get(item_id), user_data)

    def _merge_emby_user_data(self, current: Optional[Dict[str, Any]], candidate: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        current = current if isinstance(current, dict) else {}
        candidate = candidate if isinstance(candidate, dict) else {}
        if not current:
            return dict(candidate)
        if self._is_played_user_data(candidate) and not self._is_played_user_data(current):
            return dict(candidate)
        current_date = self._parse_date(current.get("LastPlayedDate"))
        candidate_date = self._parse_date(candidate.get("LastPlayedDate"))
        if candidate_date and (not current_date or candidate_date > current_date):
            merged = {**current, **candidate}
            merged["Played"] = self._to_bool(current.get("Played")) or self._to_bool(candidate.get("Played"))
            return merged
        if self._to_bool(candidate.get("Played")) and not self._to_bool(current.get("Played")):
            merged = {**current, "Played": True}
            return merged
        return current

    def _fetch_emby_item_ids(
        self,
        service: Any,
        user_id: str,
        parent_id: str,
        include_types: str,
        state_query: str,
    ) -> set:
        item_ids = set()
        if not parent_id or not include_types or not state_query:
            return item_ids
        start = 0
        limit = 500
        while True:
            url = (
                f"[HOST]emby/Users/{user_id}/Items?ParentId={quote(parent_id)}&Recursive=true"
                f"&IncludeItemTypes={include_types}&{state_query}"
                f"&Fields=UserData&EnableUserData=true&GroupItems=false&EnableTotalRecordCount=false"
                f"&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            for item in raw_items:
                item_id = self._clean_text(item.get("Id"))
                if item_id:
                    item_ids.add(item_id)
            if len(raw_items) < limit:
                break
            start += limit
        return item_ids

    def _fetch_emby_item_detail(self, service: Any, user_id: str, item_id: Any) -> Dict[str, Any]:
        clean_id = self._clean_text(item_id)
        if not clean_id:
            return {}
        fields = quote(
            "DateCreated,Path,Genres,ProviderIds,Overview,PrimaryImageAspectRatio,BasicSyncInfo,"
            "ChildCount,RecursiveItemCount,ProductionYear,CommunityRating,CriticRating,SortName,MediaSources,"
            "ParentId,PremiereDate,RunTimeTicks,ImageTags,BackdropImageTags,UserDataPlayCount,UserDataLastPlayedDate"
        )
        url = (
            f"[HOST]emby/Users/{user_id}/Items/{quote(clean_id)}"
            f"?Fields={fields}&EnableUserData=true&api_key=[APIKEY]"
        )
        response = service.get_data(url)
        data = response.json() if hasattr(response, "json") else response
        return data if isinstance(data, dict) else {}

    def _fetch_merged_emby_item_detail_user_data(self, service: Any, user_ids: List[str], item_id: Any) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        for user_id in user_ids:
            detail = self._fetch_emby_item_detail(service, user_id, item_id)
            user_data = detail.get("UserData") if isinstance(detail, dict) else None
            if isinstance(user_data, dict):
                merged = self._merge_emby_user_data(merged, user_data)
        return merged

    def _needs_emby_user_data_detail(self, item: Dict[str, Any]) -> bool:
        user_data = item.get("UserData") if isinstance(item, dict) else None
        if not isinstance(user_data, dict) or "Played" not in user_data:
            return True
        return self._to_bool(user_data.get("Played")) and not self._clean_text(user_data.get("LastPlayedDate"))

    @staticmethod
    def _library_include_types(collection_type: Any) -> str:
        library_type = str(collection_type or "").strip().lower()
        if library_type == "movies":
            return "Movie"
        if library_type == "tvshows":
            return "Series"
        return "Movie,Series"

    def _fetch_series_episode_stats(
        self,
        service: Any,
        user_ids: List[str],
        series_id: Any,
        played_episode_ids: Optional[set] = None,
        episode_user_data_by_item: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        item_id = self._clean_text(series_id)
        if not item_id:
            return {}
        user_id = user_ids[0] if user_ids else ""
        if not user_id:
            return {}
        played_episode_ids = played_episode_ids or set()
        episode_user_data_by_item = episode_user_data_by_item or {}
        total = 0
        watched = 0
        size = 0
        paths = []
        start = 0
        limit = 500
        detail_user_data_count = 0
        fields = quote(
            "Path,MediaSources,UserData,DateCreated,UserDataPlayCount,"
            "UserDataLastPlayedDate"
        )
        last_episode_added_at = ""
        last_watched_at = ""
        while True:
            url = (
                f"[HOST]emby/Shows/{quote(item_id)}/Episodes?UserId={quote(user_id)}&IsMissing=false"
                f"&Fields={fields}&EnableUserData=true&EnableTotalRecordCount=false"
                f"&StartIndex={start}&Limit={limit}&api_key=[APIKEY]"
            )
            response = service.get_data(url)
            data = response.json() if hasattr(response, "json") else response
            raw_items = data.get("Items") if isinstance(data, dict) else []
            if not raw_items:
                break
            total += len(raw_items)
            for episode in raw_items:
                episode_id = self._clean_text(episode.get("Id"))
                merged_user_data = episode_user_data_by_item.get(episode_id)
                if merged_user_data:
                    episode = {**episode, "UserData": merged_user_data}
                if self._needs_emby_user_data_detail(episode):
                    detail_user_data = self._fetch_merged_emby_item_detail_user_data(service, user_ids, episode_id)
                    if detail_user_data:
                        episode = {**episode, "UserData": detail_user_data}
                        detail_user_data_count += 1
                user_data = episode.get("UserData") or {}
                if self._is_played_user_data(user_data):
                    watched += 1
                last_episode_added_at = self._max_date_text(last_episode_added_at, self._format_emby_date(episode.get("DateCreated")))
                last_watched_at = self._max_date_text(last_watched_at, self._format_emby_date(user_data.get("LastPlayedDate")))
                path = self._map_emby_path(episode.get("Path"))
                if path:
                    paths.append(path)
                size += self._media_sources_size(episode.get("MediaSources") or [])
            if len(raw_items) < limit:
                break
            start += limit
        return {
            "total_episodes": total,
            "watched_episodes": watched,
            "size": size,
            "paths": paths,
            "last_episode_added_at": last_episode_added_at,
            "last_watched_at": last_watched_at,
            "detail_user_data_count": detail_user_data_count,
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
        watched = played
        watch_state = self._watch_state(watched)
        emby_path = self._clean_text(item.get("Path"))
        path = self._map_emby_path(emby_path)
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
            "emby_path": emby_path if emby_path and emby_path != path else "",
            "emby_path_preview": self._path_preview(emby_path) if emby_path and emby_path != path else "",
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
    def _watch_state(watched: bool) -> str:
        return "watched" if watched else "unwatched"

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

    def _build_watch_audit(self, audits: List[Dict[str, Any]], media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        media_by_library: Dict[str, List[Dict[str, Any]]] = {}
        for item in media_items:
            library_id = self._clean_text(item.get("library_id"))
            if library_id:
                media_by_library.setdefault(library_id, []).append(item)

        result = []
        for audit in audits:
            library_id = self._clean_text(audit.get("library_id"))
            library_media = media_by_library.get(library_id, [])
            plugin_played_ids = {self._clean_text(item.get("item_id")) for item in library_media if item.get("watched")}
            emby_played_ids = set(audit.get("emby_played_ids") or [])
            missing_played = sorted(emby_played_ids - plugin_played_ids)
            extra_played = sorted(plugin_played_ids - emby_played_ids)
            media_index = {self._clean_text(item.get("item_id")): item for item in library_media}
            result.append(
                {
                    **{key: value for key, value in audit.items() if not key.endswith("_ids")},
                    "media_count": len(library_media),
                    "emby_played_count": len(emby_played_ids),
                    "plugin_played_count": len(plugin_played_ids),
                    "played_match": not missing_played and not extra_played,
                    "missing_played": self._audit_samples(missing_played, media_index),
                    "extra_played": self._audit_samples(extra_played, media_index),
                }
            )
        return result

    @staticmethod
    def _log_watch_audit(audits: List[Dict[str, Any]]) -> None:
        for audit in audits:
            message = (
                f"{audit.get('server')} / {audit.get('library')}: "
                f"played source {audit.get('played_source')} "
                f"{audit.get('emby_played_count')}/{audit.get('plugin_played_count')}, "
                f"played counts {audit.get('played_source_counts')}"
            )
            if audit.get("played_match"):
                logger.debug(f"媒体库管家播放状态审计通过：{message}")
            else:
                logger.warning(f"媒体库管家播放状态审计差异：{message}")

    @staticmethod
    def _audit_samples(item_ids: List[str], media_index: Dict[str, Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
        samples = []
        for item_id in item_ids[:limit]:
            media = media_index.get(item_id) or {}
            samples.append({"item_id": item_id, "title": media.get("title") or ""})
        return samples

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
        estimated_size = self._sum_unique_target_size([item for item in plan_items if item.get("status") == "ready"])
        plan_status = "ready" if plan_items and ready_count == len(plan_items) else "empty" if not plan_items else "blocked"
        plan = {
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
        self._log_cleanup_plan(plan)
        return plan

    def _refresh_cleanup_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        plan_items = list(plan.get("items") or [])
        ready_items = [item for item in plan_items if item.get("status") == "ready"]
        ready_count = len(ready_items)
        plan_status = "ready" if plan_items and ready_count == len(plan_items) else "empty" if not plan_items else "blocked"
        plan["items"] = plan_items
        plan["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan["source_label"] = self._plan_source_label(plan.get("source") or "manual")
        plan["estimated_reclaim_size"] = self._sum_unique_target_size(ready_items)
        plan["ready_count"] = ready_count
        plan["status"] = plan_status
        plan["message"] = self._plan_message(plan_status, plan_items)
        return plan

    def _log_cleanup_plan(self, plan: Dict[str, Any]) -> None:
        recognition = self._cleanup_plan_recognition_summary(plan)
        logger.info(
            "媒体库管家清理计划生成："
            f"batch={plan.get('batch_id') or plan.get('id')}，source={plan.get('source')}，"
            f"items={len(plan.get('items') or [])}，ready={plan.get('ready_count', 0)}，"
            f"estimated={self._human_size(plan.get('estimated_reclaim_size'))}，"
            f"ai_enabled={recognition['ai_enabled']}，ai_called={recognition['ai_called']}，"
            f"ai_involved={recognition['ai_involved']}，"
            f"ai_result={recognition['ai_result']}"
        )
        for item in plan.get("items", []) or []:
            self._log_cleanup_plan_item(plan, item, "媒体库管家清理计划识别")

    def _log_cleanup_plan_item(self, plan: Dict[str, Any], item: Dict[str, Any], prefix: str) -> None:
        target_sources = self._target_source_counts(item.get("delete_targets") or [])
        logger.info(
            f"{prefix}："
            f"batch={plan.get('batch_id') or plan.get('id')}，title={item.get('title')}，"
            f"status={item.get('status')}，message={item.get('message')}，"
            f"targets={len(item.get('delete_targets') or [])}，target_sources={target_sources}，"
            f"download_tasks={len(item.get('download_tasks') or [])}，"
            f"seed_candidates={len(item.get('seed_candidates') or [])}，"
            f"ai_resource_candidates={len(item.get('ai_resource_candidates') or [])}，"
            f"ai_resource_state={item.get('ai_resource_state') or '-'}，"
            f"ai_resource_message={item.get('ai_resource_message') or '-'}"
        )

    def _cleanup_plan_recognition_summary(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        items = plan.get("items") or []
        targets = [target for item in items for target in item.get("delete_targets", []) or []]
        seed_candidates = [candidate for item in items for candidate in item.get("seed_candidates", []) or []]
        ai_resource_candidates = [candidate for item in items for candidate in item.get("ai_resource_candidates", []) or []]
        ai_states = [item.get("ai_resource_state") for item in items if item.get("ai_resource_state")]
        ai_targets = [target for target in targets if target.get("match_source") == "ai_resource_recognition"]
        ai_candidates = [candidate for candidate in seed_candidates if candidate.get("match_source") == "ai_resource_recognition"]
        ai_involved = bool(ai_targets or ai_candidates or ai_resource_candidates)
        ai_called = ai_involved or any(state in {"ai_failed", "no_ai_match"} for state in ai_states)
        if ai_involved:
            ai_result = f"AI识别目标 {len(ai_targets)} 个，保种候选 {len(ai_candidates)} 个，源文件候选 {len(ai_resource_candidates)} 个"
        elif self._config.get("ai_suggestions"):
            details = []
            no_source_count = ai_states.count("no_source_candidates")
            failed_count = ai_states.count("ai_failed")
            unavailable_count = ai_states.count("ai_unavailable")
            no_match_count = ai_states.count("no_ai_match")
            if no_source_count:
                details.append(f"无疑似源文件 {no_source_count} 个")
            if unavailable_count:
                details.append(f"智能助手未配置 {unavailable_count} 个")
            if failed_count:
                details.append(f"AI识别失败 {failed_count} 个")
            if no_match_count:
                details.append(f"AI未选中可信候选 {no_match_count} 个")
            if not details:
                details.append("本批次无需要 AI 判断的记录丢失条目")
            if seed_candidates:
                details.append(f"保种排查候选 {len(seed_candidates)} 个需用户确认")
            ai_result = "；".join(details)
        else:
            ai_result = "AI未启用"
        return {
            "ai_enabled": bool(self._config.get("ai_suggestions")),
            "ai_involved": ai_involved,
            "ai_called": ai_called,
            "ai_result": ai_result,
        }

    @staticmethod
    def _target_source_counts(targets: List[Dict[str, Any]]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for target in targets:
            source = target.get("match_source") or target.get("kind") or "unknown"
            counts[source] = counts.get(source, 0) + 1
        return counts

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
            logger.info(f"媒体库管家清理批次未生成：source={source}，当前清理规则未命中媒体")
            return None
        pending_plan = self.get_data(self.DATA_KEY_PENDING_PLAN) or {}
        overwrite_sources = overwrite_sources or {"scheduled"}
        if pending_plan and pending_plan.get("source") not in overwrite_sources:
            logger.info(
                "媒体库管家清理批次未生成："
                f"source={source}，已有不可覆盖批次 batch={pending_plan.get('batch_id') or pending_plan.get('id')}，"
                f"pending_source={pending_plan.get('source')}"
            )
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
        else:
            logger.info(
                "媒体库管家清理批次通知跳过："
                f"batch={plan.get('batch_id') or plan.get('id')}，source={source}，notify_enabled=False"
            )
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
        record_dest_targets: List[Dict[str, Any]] = []
        record_source_targets: List[Dict[str, Any]] = []
        for record in records:
            dest_fileitem = getattr(record, "dest_fileitem", None)
            src_fileitem = getattr(record, "src_fileitem", None)
            if isinstance(dest_fileitem, dict):
                record_dest_targets.append(self._target_from_history(record, "dest", dest_fileitem))
            if delete_source and isinstance(src_fileitem, dict):
                record_source_targets.append(self._target_from_history(record, "src", src_fileitem))

        mapping_targets = self._targets_from_directory_mapping(media, delete_source)
        mapping_dest_targets = [target for target in mapping_targets if target.get("kind") == "dest"]
        mapping_source_targets = [target for target in mapping_targets if target.get("kind") == "src"]
        delete_targets = list(mapping_dest_targets or record_dest_targets)
        if delete_source:
            delete_targets.extend(mapping_source_targets or record_source_targets)
        delete_targets = self._dedupe_targets(delete_targets)
        delete_targets = self._annotate_targets_for_media(self._with_scraping_targets(delete_targets), media)
        download_tasks = self._download_tasks_for_media(media, records)
        seed_candidates = [] if download_tasks else self._seed_task_candidates_from_targets(media, delete_targets)
        ai_resource_candidates: List[Dict[str, Any]] = []
        ai_resource_state = ""
        ai_resource_message = ""

        has_source_target = any(target.get("kind") == "src" for target in delete_targets)
        has_media_library_target = any(target.get("kind") == "dest" for target in delete_targets)
        source_record_missing = delete_source and has_media_library_target and not has_source_target
        status = "ready" if has_media_library_target else "no_match"
        if source_record_missing:
            if self._ai_resource_recognition_enabled():
                ai_result = self._ai_resource_recognition_for_record_missing(media, delete_targets)
                ai_resource_candidates = ai_result["candidates"]
                ai_resource_state = ai_result["state"]
                ai_resource_message = ai_result["message"]
            elif self._config.get("ai_suggestions"):
                ai_resource_state = "ai_unavailable"
                ai_resource_message = self._ai_agent_status()[1]
        if records and delete_targets:
            message = "已匹配整理记录。"
        elif source_record_missing:
            message = "整理记录或源文件记录缺失，已定位媒体库文件，将按确认范围删除媒体库文件。"
        elif delete_targets:
            dest_count = len([target for target in delete_targets if target.get("kind") == "dest"])
            src_count = len([target for target in delete_targets if target.get("kind") == "src"])
            message = f"整理记录丢失，已按目录映射识别 {dest_count} 个媒体库文件、{src_count} 个源文件，请审核后执行。"
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
            "volume_name": media.get("volume_name"),
            "volume_free_percent": media.get("volume_free_percent"),
            "volume_summary": media.get("volume_summary"),
            "volumes": media.get("volumes") or [],
            "root_directories": media.get("root_directories") or [],
            "matched_transfer_records": [self._transfer_record_summary(record) for record in records],
            "download_tasks": download_tasks,
            "seed_candidates": seed_candidates,
            "ai_resource_candidates": ai_resource_candidates,
            "ai_resource_state": ai_resource_state,
            "ai_resource_message": ai_resource_message,
            "delete_targets": self._dedupe_targets(delete_targets),
            "status": status,
            "message": message,
        }

    def _annotate_targets_for_media(self, targets: List[Dict[str, Any]], media: Dict[str, Any]) -> List[Dict[str, Any]]:
        for target in targets:
            target["media_id"] = media.get("id")
            target["media_title"] = media.get("title")
            target["media_type"] = media.get("type")
            target["media_type_label"] = media.get("type_label")
        return targets

    def _seed_task_candidates_from_targets(self, media: Dict[str, Any], targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        mappings = self._config.get("downloader_path_mappings") or []
        if not mappings:
            return []
        candidates: List[Dict[str, Any]] = []
        seen = set()
        for target in targets:
            if target.get("kind") != "src":
                continue
            source_path = self._normalized_path_text(target.get("path"))
            if not source_path:
                continue
            for mapping in mappings:
                resource_path = self._clean_text(mapping.get("resource_path"))
                if not self._path_is_relative_to(source_path, resource_path):
                    continue
                relative_path = self._relative_path(source_path, resource_path)
                downloader_path = self._join_path(mapping.get("downloader_path"), relative_path)
                key = (mapping.get("downloader"), downloader_path)
                if not downloader_path or key in seen:
                    continue
                seen.add(key)
                candidates.append({
                    "title": media.get("title"),
                    "media_id": media.get("id"),
                    "downloader": mapping.get("downloader"),
                    "source_path": source_path,
                    "downloader_path": downloader_path,
                    "reason": "整理记录或下载历史未提供 download hash，已按下载器目录映射生成候选路径，需 AI/人工确认对应下载任务。",
                    "status": "needs_review",
                })
        return candidates

    def _ai_resource_recognition_for_record_missing(self, media: Dict[str, Any], targets: List[Dict[str, Any]]) -> Dict[str, Any]:
        source_candidates = self._source_file_candidates_from_directory_mapping(media, targets)
        if not source_candidates:
            logger.info(f"媒体库管家 AI资源任务识别：title={media.get('title')}，未找到可交给 AI 判断的疑似源文件")
            return {"state": "no_source_candidates", "message": "无疑似源文件", "candidates": []}
        ai_selected, error = self._select_source_candidates_with_ai(media, source_candidates)
        if error:
            return {"state": "ai_failed", "message": f"AI识别失败：{error}", "candidates": []}
        state = "selected" if ai_selected else "no_ai_match"
        message = f"AI识别到 {len(ai_selected)} 个候选源文件" if ai_selected else "AI未选中可信候选源文件"
        logger.info(
            "媒体库管家 AI资源任务识别结果："
            f"title={media.get('title')}，candidates={len(source_candidates)}，selected={len(ai_selected)}，"
            f"result={self._json_dumps(ai_selected[:5])}"
        )
        return {"state": state, "message": message, "candidates": ai_selected}

    def _source_file_candidates_from_directory_mapping(self, media: Dict[str, Any], targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        storage = StorageChain()
        mappings = self._directory_mappings()
        candidates: List[Dict[str, Any]] = []
        seen = set()
        dest_paths = [
            self._normalized_path_text(target.get("path"))
            for target in targets
            if target.get("kind") == "dest" and self._normalized_path_text(target.get("path"))
        ] or self._media_file_paths(media)
        for media_path in dest_paths:
            mapping = self._match_directory_mapping(media_path, mappings)
            if not mapping:
                continue
            expected_path = self._mapped_source_path(media_path, mapping)
            expected_parent = str(Path(expected_path).parent) if expected_path else ""
            if not expected_parent:
                continue
            storage_name = self._clean_text(getattr(mapping, "storage", "")) or "local"
            try:
                parent_item = storage.get_file_item(storage=storage_name, path=Path(expected_parent))
                siblings = storage.list_files(parent_item, recursion=False) if parent_item else []
            except Exception as err:
                logger.warning(f"媒体库管家 AI资源任务识别读取源目录失败：path={expected_parent}，error={err}")
                siblings = []
            for sibling in siblings or []:
                sibling_item = self._fileitem_to_dict(sibling)
                sibling_path = self._normalized_path_text(sibling_item.get("path"))
                if not sibling_path or not self._is_media_file_path(sibling_path):
                    continue
                key = sibling_path.lower()
                if key in seen:
                    continue
                seen.add(key)
                candidates.append({
                    "title": media.get("title"),
                    "media_id": media.get("id"),
                    "type_label": media.get("type_label"),
                    "source_path": sibling_path,
                    "filename": Path(sibling_path).name,
                    "size": self._to_int(sibling_item.get("size") or sibling_item.get("size_bytes"), 0),
                    "expected_path": expected_path,
                    "media_path": media_path,
                    "match_source": "directory_mapping_candidate",
                    "status": "ai_pending",
                })
        return sorted(candidates, key=lambda item: item.get("size") or 0, reverse=True)[:20]

    def _select_source_candidates_with_ai(self, media: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
        try:
            response_text = self._run_async(self._ask_llm_for_source_candidates(media, candidates))
            selected = self._parse_ai_candidate_response(response_text, candidates)
        except Exception as err:
            error = self._clean_text(err)
            logger.warning(f"媒体库管家 AI资源任务识别调用失败：title={media.get('title')}，error={error}")
            return [], error
        return selected, ""

    async def _ask_llm_for_source_candidates(self, media: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
        from app.agent.llm import LLMHelper

        payload = {
            "media": {
                "title": media.get("title"),
                "year": media.get("year"),
                "type": media.get("type"),
                "type_label": media.get("type_label"),
                "library_path": media.get("path") or media.get("path_preview"),
            },
            "candidates": [
                {
                    "index": index,
                    "filename": candidate.get("filename"),
                    "source_path": candidate.get("source_path"),
                    "size": candidate.get("size"),
                    "expected_path": candidate.get("expected_path"),
                }
                for index, candidate in enumerate(candidates, 1)
            ],
        }
        prompt = (
            "你是 MoviePilot 媒体整理助手。请根据媒体标题、年份、媒体库路径和候选源文件路径，"
            "判断哪些候选最可能是该媒体对应的源文件。只输出 JSON，不要解释。"
            "JSON 格式：{\"selected\":[{\"index\":1,\"confidence\":0.0-1.0,\"reason\":\"简短中文原因\"}]}。"
            "如果没有可信候选，输出 {\"selected\":[]}。\n"
            f"{self._json_dumps(payload)}"
        )
        llm = await LLMHelper.get_llm(streaming=False)
        response = await asyncio.wait_for(llm.ainvoke(prompt), timeout=45)
        return self._clean_text(getattr(response, "content", response))

    def _parse_ai_candidate_response(self, response_text: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        payload = self._extract_json_object(response_text)
        selected = payload.get("selected") if isinstance(payload, dict) else []
        if not isinstance(selected, list):
            return []
        result: List[Dict[str, Any]] = []
        for item in selected[:5]:
            if not isinstance(item, dict):
                continue
            index = self._to_int(item.get("index"), 0)
            if index < 1 or index > len(candidates):
                continue
            confidence = float(item.get("confidence") or 0)
            if confidence < 0.6:
                continue
            candidate = candidates[index - 1]
            result.append({
                **candidate,
                "confidence": round(confidence, 3),
                "reason": self._clean_text(item.get("reason")) or "AI判断为疑似源文件",
                "match_source": "ai_resource_recognition",
                "match_source_label": "AI识别",
                "status": "needs_review",
            })
        return result

    @staticmethod
    def _extract_json_object(text: str) -> Dict[str, Any]:
        clean_text = str(text or "").strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            if clean_text.lower().startswith("json"):
                clean_text = clean_text[4:].strip()
        start = clean_text.find("{")
        end = clean_text.rfind("}")
        if start >= 0 and end >= start:
            clean_text = clean_text[start:end + 1]
        return json.loads(clean_text)

    @staticmethod
    def _run_async(coro: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(lambda: asyncio.run(coro)).result()

    @staticmethod
    def _json_dumps(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

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
            "filename": Path(path).name,
            "size": size,
            "fileitem": fileitem,
            "match_source": "directory_mapping",
            "match_source_label": "目录映射识别",
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

    def _with_scraping_targets(self, targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not targets:
            return targets
        storage = StorageChain()
        result = list(targets)
        seen_paths = {self._normalized_path_text(target.get("path")).lower() for target in result if target.get("path")}
        for target in targets:
            if target.get("kind") != "dest" or not self._is_media_file_path(target.get("path")):
                continue
            for scraping_target in self._scraping_targets_for_media_target(storage, target):
                key = self._normalized_path_text(scraping_target.get("path")).lower()
                if not key or key in seen_paths:
                    continue
                seen_paths.add(key)
                result.append(scraping_target)
        return result

    def _scraping_targets_for_media_target(self, storage: StorageChain, target: Dict[str, Any]) -> List[Dict[str, Any]]:
        path = self._normalized_path_text(target.get("path"))
        fileitem = target.get("fileitem") or {}
        storage_name = self._clean_text(fileitem.get("storage")) or "local"
        if not path:
            return []
        try:
            parent_item = storage.get_file_item(storage=storage_name, path=Path(path).parent)
            if not parent_item:
                return []
            siblings = storage.list_files(parent_item, recursion=False) or []
        except Exception as err:
            logger.warning(f"媒体库管家读取同名刮削文件失败 {path}: {err}")
            return []
        stem = Path(path).stem.lower()
        result: List[Dict[str, Any]] = []
        for sibling in siblings:
            sibling_item = self._fileitem_to_dict(sibling)
            sibling_path = self._normalized_path_text(sibling_item.get("path"))
            sibling_name = Path(sibling_path).name if sibling_path else self._clean_text(sibling_item.get("name"))
            if not sibling_path or not sibling_name:
                continue
            sibling_path_obj = Path(sibling_path)
            if sibling_path_obj.stem.lower() != stem:
                continue
            if sibling_path_obj.suffix.lower() not in self.SCRAPING_FILE_EXTENSIONS:
                continue
            size = self._to_int(sibling_item.get("size") or sibling_item.get("size_bytes"), 0)
            result.append({
                "record_id": target.get("record_id"),
                "kind": "dest_scraping",
                "kind_label": "刮削伴随文件",
                "path": sibling_path,
                "path_preview": self._path_preview(sibling_path),
                "size": size,
                "fileitem": sibling_item,
                "match_source": "scraping_sidecar",
                "parent_media_path": path,
            })
        return result

    @classmethod
    def _is_media_file_path(cls, path: Any) -> bool:
        return Path(str(path or "")).suffix.lower() in cls.MEDIA_FILE_EXTENSIONS

    @staticmethod
    def _fileitem_to_dict(fileitem: Any) -> Dict[str, Any]:
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

    def _map_emby_path(self, path: Any) -> str:
        return self._apply_path_mappings(path, self._config.get("path_mappings") or [])

    @classmethod
    def _apply_path_mappings(cls, path: Any, mappings: List[Dict[str, str]]) -> str:
        clean_path = cls._normalized_path_text(path)
        if not clean_path:
            return ""
        for mapping in mappings or []:
            emby_root = cls._normalized_path_text((mapping or {}).get("emby_path"))
            mp_root = cls._normalized_path_text((mapping or {}).get("mp_path"))
            if not emby_root or not mp_root:
                continue
            if clean_path == emby_root:
                return mp_root
            if clean_path.startswith(emby_root + "/"):
                return f"{mp_root}/{clean_path[len(emby_root) + 1:]}"
        return clean_path

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

    @classmethod
    def _join_path(cls, root: Any, relative_path: Any) -> str:
        clean_root = cls._normalized_path_text(root)
        clean_relative = cls._normalized_path_text(relative_path).lstrip("/")
        if not clean_root:
            return ""
        if not clean_relative:
            return clean_root
        return f"{clean_root}/{clean_relative}"

    @staticmethod
    def _normalized_path_text(path: Any) -> str:
        return str(path or "").strip().replace("\\", "/").rstrip("/")

    def _match_transfer_records(self, media: Dict[str, Any]) -> List[Any]:
        records: List[Any] = []
        title = self._clean_text(media.get("title"))
        tmdbid = self._clean_text((media.get("provider_ids") or {}).get("Tmdb"))
        if tmdbid:
            records.extend(self._query_transfer_by_tmdb(tmdbid, media.get("type")))
        if title:
            records.extend(self._query_transfer_by_title(title))

        paths = self._media_file_paths(media)
        matched = []
        for record in self._dedupe_records(records):
            if not bool(getattr(record, "status", True)):
                continue
            if tmdbid and str(getattr(record, "tmdbid", "") or "") == tmdbid:
                matched.append(record)
                continue
            if any(
                self._path_matches(path, record_path)
                for path in paths
                for record_path in self._record_dest_paths(record)
            ):
                matched.append(record)
        return self._dedupe_records(matched)

    def _record_dest_paths(self, record: Any) -> List[str]:
        paths = [self._clean_text(getattr(record, "dest", ""))]
        fileitem = getattr(record, "dest_fileitem", None)
        if isinstance(fileitem, dict):
            paths.append(self._clean_text(fileitem.get("path")))
        return [path for path in paths if path]

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

    def _download_tasks_for_media(self, media: Dict[str, Any], records: List[Any]) -> List[Dict[str, Any]]:
        tasks = self._attach_candidate_downloaders(self._dedupe_download_tasks([
            *self._download_tasks_from_records(records),
            *self._download_tasks_from_history(media, records),
        ]))
        return self._expand_related_download_tasks(self._enrich_download_tasks_from_configured_downloaders(tasks))

    def _download_tasks_from_records(self, records: List[Any]) -> List[Dict[str, Any]]:
        tasks = []
        for record in records:
            downloader = self._clean_text(getattr(record, "downloader", ""))
            download_hash = self._clean_text(getattr(record, "download_hash", ""))
            if not download_hash:
                continue
            tasks.append({
                "record_id": getattr(record, "id", None),
                "title": self._clean_text(getattr(record, "title", "")),
                "downloader": "",
                "original_downloader": downloader,
                "downloader_type": "",
                "download_hash": download_hash,
                "downloader_match_source": "history_hash",
                "downloader_lookup_state": "history_hash_only",
                "matched_paths": [self._clean_text(getattr(record, "dest", ""))],
                "source": "transfer_history",
            })
        return self._dedupe_download_tasks(tasks)

    def _download_tasks_from_history(self, media: Dict[str, Any], records: List[Any]) -> List[Dict[str, Any]]:
        if not DownloadHistoryOper:
            return []
        oper = DownloadHistoryOper()
        history_items: List[Any] = []
        for path in self._media_file_paths(media):
            history_items.extend(self._query_download_history_by_path(oper, path))
        tmdbid = self._clean_text((media.get("provider_ids") or {}).get("Tmdb"))
        if tmdbid and hasattr(oper, "get_by_mediaid"):
            try:
                media_history = oper.get_by_mediaid(tmdbid=int(tmdbid), doubanid=self._clean_text((media.get("provider_ids") or {}).get("Douban")))
            except Exception:
                media_history = []
            if isinstance(media_history, list):
                history_items.extend(media_history)
            elif media_history:
                history_items.append(media_history)
        title = self._clean_text(media.get("title"))
        if title and hasattr(oper, "get_last_by"):
            mtype = "MOV" if media.get("type") == "movie" else "TV"
            try:
                item = oper.get_last_by(mtype=mtype, title=title, year=self._clean_text(media.get("year")), tmdbid=int(tmdbid) if tmdbid else None)
            except Exception:
                item = None
            if isinstance(item, list):
                history_items.extend(item)
            elif item:
                history_items.append(item)

        record_ids = {getattr(record, "id", None) for record in records if getattr(record, "id", None) is not None}
        tasks: List[Dict[str, Any]] = []
        for item in self._dedupe_records(history_items):
            downloader = self._clean_text(getattr(item, "downloader", ""))
            download_hash = self._clean_text(getattr(item, "download_hash", "")) or self._clean_text(getattr(item, "hash", ""))
            if not download_hash:
                continue
            record_id = getattr(item, "transfer_id", None) or getattr(item, "transferhis_id", None)
            if record_id not in record_ids:
                record_id = None
            fullpath = self._clean_text(getattr(item, "fullpath", ""))
            matched_paths = [fullpath] if fullpath else [
                self._clean_text(getattr(item, attr, ""))
                for attr in ["path", "save_path", "savepath"]
                if self._clean_text(getattr(item, attr, ""))
            ]
            tasks.append({
                "record_id": record_id,
                "title": self._clean_text(getattr(item, "title", "")) or self._clean_text(getattr(item, "torrentname", "")) or title,
                "downloader": "",
                "original_downloader": downloader,
                "downloader_type": "",
                "download_hash": download_hash,
                "downloader_match_source": "history_hash",
                "downloader_lookup_state": "history_hash_only",
                "matched_paths": matched_paths,
                "source": "download_history",
            })
        return self._dedupe_download_tasks(tasks)

    def _query_download_history_by_path(self, oper: Any, path: str) -> List[Any]:
        result: List[Any] = []
        clean_path = self._normalized_path_text(path)
        if not clean_path:
            return result
        if hasattr(oper, "get_file_by_fullpath"):
            try:
                item = oper.get_file_by_fullpath(fullpath=clean_path)
            except TypeError:
                try:
                    item = oper.get_file_by_fullpath(clean_path)
                except Exception:
                    item = None
            except Exception:
                item = None
            if item:
                result.append(item)
        if hasattr(oper, "get_files_by_savepath"):
            save_path = str(Path(clean_path).parent)
            try:
                items = oper.get_files_by_savepath(fullpath=save_path)
            except TypeError:
                try:
                    items = oper.get_files_by_savepath(save_path)
                except Exception:
                    items = []
            except Exception:
                items = []
            if items:
                result.extend(items)
        if hasattr(oper, "list_by_path"):
            try:
                items = oper.list_by_path(path=clean_path)
            except Exception:
                items = []
            if items:
                result.extend(items)
        return result

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
            key = str(task.get("download_hash") or "").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            result.append(task)
        return result

    def _attach_candidate_downloaders(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates = sorted(self._selected_downloader_names())
        for task in tasks:
            task["candidate_downloaders"] = candidates
        return tasks

    def _enrich_download_tasks_from_configured_downloaders(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not tasks:
            return tasks
        candidates = self._configured_seed_cleanup_downloaders(DownloaderHelper())
        candidate_names = [downloader for downloader, _ in candidates]
        for task in tasks:
            download_hash = self._clean_text(task.get("download_hash"))
            if not download_hash:
                continue
            task["candidate_downloaders"] = candidate_names
            for downloader, service_info in candidates:
                module = getattr(service_info, "module", None)
                if not module:
                    continue
                torrent = self._find_downloader_torrent(service_info, downloader, download_hash)
                if not torrent:
                    continue
                summary = self._downloader_torrent_summary(torrent)
                task.update({
                    "downloader": downloader,
                    "downloader_type": self._clean_text(getattr(service_info, "type", "")),
                    "task_name": summary.get("name"),
                    "save_path": summary.get("save_path"),
                    "content_path": summary.get("content_path"),
                    "task_state": summary.get("state"),
                    "task_size": summary.get("size"),
                    "matched_downloader": downloader,
                    "downloader_match_source": "configured_downloader",
                    "downloader_lookup_state": "matched" if summary.get("name") else "matched_without_name",
                })
                logger.info(
                    f"媒体库管家保种任务识别：hash={download_hash}，downloader={downloader}，"
                    f"task_name={task.get('task_name') or '-'}"
                )
                break
            if not task.get("matched_downloader"):
                logger.warning(
                    f"媒体库管家保种任务未读取到配置下载器实时信息：hash={download_hash}，"
                    f"history_downloader={task.get('original_downloader') or '-'}，candidates={candidate_names}"
                )
        return tasks

    def _expand_related_download_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not tasks:
            return tasks
        helper = DownloaderHelper()
        candidates = dict(self._configured_seed_cleanup_downloaders(helper))
        expanded = list(tasks)
        seen_hashes = {self._clean_text(task.get("download_hash")).lower() for task in tasks if task.get("download_hash")}
        for task in tasks:
            downloader = self._clean_text(task.get("matched_downloader") or task.get("downloader"))
            download_hash = self._clean_text(task.get("download_hash"))
            if not downloader or not download_hash:
                continue
            service_info = candidates.get(downloader)
            module = getattr(service_info, "module", None) if service_info else None
            if not module or not hasattr(module, "list_torrents"):
                continue
            related = self._related_downloader_torrents(module, downloader, task)
            for torrent in related:
                torrent_hash = self._clean_text(self._object_value(torrent, "hash", "hashString", "hash_string")).lower()
                if not torrent_hash or torrent_hash in seen_hashes:
                    continue
                summary = self._downloader_torrent_summary(torrent)
                expanded.append({
                    **task,
                    "title": summary.get("name") or task.get("title"),
                    "download_hash": torrent_hash,
                    "task_name": summary.get("name"),
                    "save_path": summary.get("save_path"),
                    "content_path": summary.get("content_path"),
                    "task_state": summary.get("state"),
                    "task_size": summary.get("size"),
                    "source": "related_seed_task",
                    "source_label": "同资源保种",
                    "related_to_hash": download_hash,
                    "downloader_match_source": "configured_downloader",
                    "downloader_lookup_state": "related_seed_task",
                })
                seen_hashes.add(torrent_hash)
                logger.info(
                    f"媒体库管家保种任务联动识别：downloader={downloader}，"
                    f"base_hash={download_hash}，related_hash={torrent_hash}，task_name={summary.get('name') or '-'}"
                )
        return self._dedupe_download_tasks(expanded)

    def _related_downloader_torrents(self, module: Any, downloader: str, task: Dict[str, Any]) -> List[Any]:
        try:
            torrents = module.list_torrents(downloader=downloader, include_all_tags=True) or []
        except Exception as err:
            logger.warning(f"媒体库管家保种任务联动读取失败：downloader={downloader}，hash={task.get('download_hash')}，error={err}")
            return []
        base_hash = self._clean_text(task.get("download_hash")).lower()
        base_names = {
            self._normalized_seed_task_name(value)
            for value in [task.get("task_name"), task.get("title")]
            if self._normalized_seed_task_name(value)
        }
        base_paths = {
            self._normalized_path_text(value).lower()
            for value in [task.get("content_path")]
            if self._normalized_path_text(value)
        }
        related = []
        for torrent in torrents:
            torrent_hash = self._clean_text(self._object_value(torrent, "hash", "hashString", "hash_string")).lower()
            if not torrent_hash or torrent_hash == base_hash:
                continue
            summary = self._downloader_torrent_summary(torrent)
            torrent_name = self._normalized_seed_task_name(summary.get("name"))
            torrent_path = self._normalized_path_text(summary.get("content_path")).lower()
            if (torrent_path and torrent_path in base_paths) or (torrent_name and torrent_name in base_names):
                related.append(torrent)
        return related

    @staticmethod
    def _normalized_seed_task_name(value: Any) -> str:
        return " ".join(str(value or "").strip().lower().split())

    def _find_downloader_torrent(self, service_info: Any, downloader: str, download_hash: str) -> Optional[Any]:
        module = getattr(service_info, "module", None)
        torrent = self._find_downloader_torrent_via_moviepilot_module(module, downloader, download_hash)
        if torrent:
            return torrent
        instance = getattr(service_info, "instance", None)
        return self._find_downloader_torrent_via_get_torrents(instance or module, download_hash)

    def _find_downloader_torrent_via_moviepilot_module(self, module: Any, downloader: str, download_hash: str) -> Optional[Any]:
        if not module or not hasattr(module, "list_torrents"):
            return None
        for hashs in [download_hash, [download_hash]]:
            try:
                torrents = module.list_torrents(hashs=hashs, downloader=downloader, include_all_tags=True)
            except Exception as err:
                logger.warning(
                    f"媒体库管家保种任务识别读取 MoviePilot 下载器任务失败：downloader={downloader}，"
                    f"hash={download_hash}，hashs={hashs}，error={err}"
                )
                continue
            torrent = self._match_downloader_torrent(torrents or [], download_hash, targeted=True)
            if torrent:
                logger.info(f"媒体库管家保种任务识别命中 MoviePilot 下载器任务：downloader={downloader}，hash={download_hash}")
                return torrent
        return None

    def _find_downloader_torrent_via_get_torrents(self, module: Any, download_hash: str) -> Optional[Any]:
        if not module or not hasattr(module, "get_torrents"):
            return None
        clean_hash = download_hash.lower()
        for args, targeted in [
            ({"ids": download_hash}, True),
            ({"ids": [download_hash]}, True),
            ({}, False),
        ]:
            torrents = self._query_downloader_torrents(module, download_hash, args)
            if not torrents:
                continue
            torrent = self._match_downloader_torrent(torrents, clean_hash, targeted=targeted)
            if torrent:
                return torrent
        return None

    def _match_downloader_torrent(self, torrents: List[Any], download_hash: str, targeted: bool = False) -> Optional[Any]:
        clean_hash = self._clean_text(download_hash).lower()
        for torrent in torrents:
            torrent_hash = self._clean_text(self._object_value(torrent, "hash", "hashString", "hash_string")).lower()
            if torrent_hash == clean_hash or (targeted and not torrent_hash and len(torrents) == 1):
                return torrent
        return None

    def _query_downloader_torrents(self, module: Any, download_hash: str, args: Dict[str, Any]) -> List[Any]:
        try:
            result = module.get_torrents(**args)
        except Exception as err:
            logger.warning(f"媒体库管家保种任务识别读取下载器失败：hash={download_hash}，args={args}，error={err}")
            return []
        if isinstance(result, tuple):
            torrents, has_error = result
            if has_error:
                logger.warning(f"媒体库管家保种任务识别读取下载器返回错误：hash={download_hash}，args={args}")
                return []
        else:
            torrents = result
        return torrents if isinstance(torrents, list) else list(torrents or [])

    def _downloader_torrent_summary(self, torrent: Any) -> Dict[str, Any]:
        return {
            "name": self._clean_text(self._object_value(torrent, "title", "name")),
            "save_path": self._clean_text(self._object_value(torrent, "save_path", "savePath", "downloadDir", "download_dir")),
            "content_path": self._clean_text(self._object_value(torrent, "content_path", "path")),
            "state": self._clean_text(self._object_value(torrent, "state", "status")),
            "size": self._to_int(self._object_value(torrent, "size", "totalSize", "total_size"), 0),
        }

    @staticmethod
    def _object_value(source: Any, *keys: str) -> Any:
        for key in keys:
            if isinstance(source, dict) and key in source:
                return source.get(key)
            if hasattr(source, "get"):
                try:
                    value = source.get(key)
                    if value not in (None, ""):
                        return value
                except Exception:
                    pass
            if hasattr(source, key):
                value = getattr(source, key)
                if value not in (None, ""):
                    return value
        return None

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
        for record_id in self._matched_record_ids_for_deleted_items(plan, deleted_targets, failed_targets):
            record_status.setdefault(record_id, True)
        deleted_seed_tasks, failed_seed_tasks = self._delete_seed_tasks(plan, record_status, deleted_targets)
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
        deleted_counts = self._deleted_target_counts(deleted_targets)
        return {
            "plan_id": plan.get("id"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success" if success else "failed",
            "delete_source": bool(plan.get("delete_source")),
            "reclaim_size": reclaim_size,
            "deleted_records": deleted_records,
            "deleted_media_files": deleted_counts["media_files"],
            "deleted_scraping_files": deleted_counts["scraping_files"],
            "deleted_source_files": deleted_counts["source_files"],
            "deleted_seed_tasks": deleted_seed_tasks,
            "failed_seed_tasks": failed_seed_tasks,
            "deleted_targets": deleted_targets,
            "failed_targets": failed_targets,
            "items": [{"title": item.get("title"), "type": item.get("type"), "size": item.get("size")} for item in executable_items],
            "message": f"清理完成，媒体库文件 {deleted_counts['media_files']} 个，刮削伴随文件 {deleted_counts['scraping_files']} 个，源文件 {deleted_counts['source_files']} 个，整理记录 {deleted_records} 条{seed_task_text}。" if success else f"清理未完全成功，失败 {len(failed_targets)} 项，请查看执行记录。",
        }

    def _matched_record_ids_for_deleted_items(
        self,
        plan: Dict[str, Any],
        deleted_targets: List[Dict[str, Any]],
        failed_targets: List[Dict[str, Any]],
    ) -> set:
        deleted_media_ids = {
            target.get("media_id")
            for target in deleted_targets
            if target.get("media_id") and target.get("kind") in {"dest", "dest_scraping", "src"}
        }
        failed_media_ids = {
            target.get("media_id")
            for target in failed_targets
            if target.get("media_id") and target.get("kind") in {"dest", "dest_scraping", "src"}
        }
        record_ids = set()
        for item in plan.get("items", []) or []:
            media_id = item.get("media_id")
            if not media_id or media_id not in deleted_media_ids or media_id in failed_media_ids:
                continue
            for record in item.get("matched_transfer_records", []) or []:
                record_id = record.get("id") or record.get("record_id")
                if record_id is not None:
                    record_ids.add(record_id)
        if record_ids:
            logger.info(f"媒体库管家整理记录联动清理：plan={plan.get('id')}，records={len(record_ids)}")
        return record_ids

    @staticmethod
    def _deleted_target_counts(deleted_targets: List[Dict[str, Any]]) -> Dict[str, int]:
        return {
            "media_files": len([target for target in deleted_targets if target.get("kind") == "dest"]),
            "scraping_files": len([target for target in deleted_targets if target.get("kind") == "dest_scraping"]),
            "source_files": len([target for target in deleted_targets if target.get("kind") == "src"]),
        }

    def _delete_seed_tasks(self, plan: Dict[str, Any], record_status: Dict[Any, bool], deleted_targets: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self._config.get("delete_seed_tasks"):
            return [], []
        successful_record_ids = {record_id for record_id, ok in record_status.items() if ok and record_id is not None}
        deleted_dest_paths = [target.get("path") for target in deleted_targets if target.get("kind") in {"dest", "dest_scraping"}]
        tasks = self._dedupe_download_tasks([
            task
            for item in plan.get("items", [])
            for task in item.get("download_tasks", []) or []
            if task.get("record_id") in successful_record_ids or self._download_task_matches_deleted_paths(task, deleted_dest_paths)
        ])
        if not tasks:
            logger.info(
                f"媒体库管家保种任务删除：未找到可删除任务，plan={plan.get('id')}，"
                f"successful_records={len(successful_record_ids)}，deleted_dest_paths={len(deleted_dest_paths)}"
            )
            return [], []

        helper = DownloaderHelper()
        deleted: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        logger.info(f"媒体库管家保种任务删除开始：plan={plan.get('id')}，tasks={len(tasks)}")
        for task in tasks:
            try:
                deleted.append(self._delete_seed_task_from_configured_downloaders(helper, task))
            except Exception as err:
                logger.warning(
                    f"媒体库管家保种任务删除失败：title={task.get('title')}，hash={task.get('download_hash')}，"
                    f"original_downloader={task.get('original_downloader') or task.get('downloader')}，error={err}"
                )
                failed.append({**task, "error": str(err)})
        logger.info(f"媒体库管家保种任务删除结束：plan={plan.get('id')}，deleted={len(deleted)}，failed={len(failed)}")
        return deleted, failed

    def _delete_seed_task_from_configured_downloaders(self, helper: DownloaderHelper, task: Dict[str, Any]) -> Dict[str, Any]:
        download_hash = self._clean_text(task.get("download_hash"))
        if not download_hash:
            raise RuntimeError("Missing download hash")
        candidates = self._configured_seed_cleanup_downloaders(helper)
        if not candidates:
            logger.warning(
                f"媒体库管家保种任务删除：没有可用下载器，title={task.get('title')}，"
                f"hash={download_hash}，configured={self._config.get('downloaders') or []}"
            )
            raise RuntimeError("No configured downloader can remove torrents")

        deleted_downloaders: List[str] = []
        attempts: List[str] = []
        original_downloader = self._clean_text(task.get("original_downloader") or task.get("downloader"))
        candidate_names = [downloader for downloader, _ in candidates]
        logger.info(
            f"媒体库管家保种任务删除尝试：title={task.get('title')}，hash={download_hash}，"
            f"original_downloader={original_downloader}，candidates={candidate_names}"
        )
        for downloader, service_info in candidates:
            module = getattr(service_info, "module", None)
            if not module or not hasattr(module, "remove_torrents"):
                attempts.append(f"{downloader}: remove_torrents unavailable")
                logger.warning(
                    f"媒体库管家保种任务删除跳过：downloader={downloader}，hash={download_hash}，"
                    "reason=remove_torrents unavailable"
                )
                continue
            try:
                logger.info(f"媒体库管家保种任务删除调用：downloader={downloader}，hash={download_hash}，delete_file=False")
                result = module.remove_torrents(
                    hashs=[download_hash],
                    delete_file=False,
                    downloader=downloader,
                )
            except Exception as err:
                attempts.append(f"{downloader}: {err}")
                logger.warning(f"媒体库管家保种任务删除异常：downloader={downloader}，hash={download_hash}，error={err}")
                continue
            if result is True:
                deleted_downloaders.append(downloader)
                logger.info(f"媒体库管家保种任务删除返回成功：downloader={downloader}，hash={download_hash}")
            else:
                attempts.append(f"{downloader}: returned failure")
                logger.warning(
                    f"媒体库管家保种任务删除返回失败：downloader={downloader}，hash={download_hash}，result={result}"
                )

        if not deleted_downloaders:
            raise RuntimeError("; ".join(attempts) or "Downloader returned failure")

        return {
            **task,
            "downloader": ",".join(deleted_downloaders),
            "original_downloader": original_downloader,
            "delete_attempts": attempts,
        }

    def _configured_seed_cleanup_downloaders(self, helper: DownloaderHelper) -> List[Tuple[str, Any]]:
        configured = list(self._config.get("downloaders") or [])
        if not configured:
            configured = [option["value"] for option in self._downloader_options() if option.get("value")]
        result: List[Tuple[str, Any]] = []
        seen = set()
        for downloader in configured:
            if not downloader or downloader in seen:
                continue
            seen.add(downloader)
            try:
                service_info = helper.get_service(name=downloader)
            except Exception as err:
                logger.warning(f"媒体库管家保种任务删除：读取下载器失败，downloader={downloader}，error={err}")
                continue
            dtype = self._clean_text(getattr(service_info, "type", "")).lower() if service_info else ""
            if dtype in self.SUPPORTED_DOWNLOADER_TYPES:
                result.append((downloader, service_info))
            else:
                logger.warning(f"媒体库管家保种任务删除：下载器不可用或类型不支持，downloader={downloader}，type={dtype}")
        return result

    def _download_task_matches_deleted_paths(self, task: Dict[str, Any], deleted_paths: List[Any]) -> bool:
        matched_paths = task.get("matched_paths") or []
        return any(
            self._path_matches(self._clean_text(deleted_path), self._clean_text(matched_path))
            for deleted_path in deleted_paths
            for matched_path in matched_paths
        )

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
        self._post_cleanup_message(title=title, text="\n".join(lines))

    def _notify_cleanup_batch(self, plan: Dict[str, Any]) -> None:
        items = plan.get("items") or []
        recorded_count = len([item for item in items if item.get("matched_transfer_records")])
        missing_count = max(0, len(items) - recorded_count)
        link = self._cleanup_page_url()
        lines = [
            f"批次：{plan.get('batch_id') or plan.get('id')}",
            f"命中媒体：{len(items)} 个，有记录：{recorded_count} 个，记录丢失：{missing_count} 个",
            f"预计可释放：{self._human_size(plan.get('estimated_reclaim_size'))}",
            "请在媒体库管家审核删除目标后确认执行。",
            "-------------------",
        ]
        lines.append("清理明细：")
        for item in items[:12]:
            title = self._clean_text(item.get("title")) or "-"
            type_label = self._clean_text(item.get("type_label")) or ("电影" if item.get("type") == "movie" else "剧集")
            record_label = "有记录" if item.get("matched_transfer_records") else "记录丢失"
            target_count = len(item.get("delete_targets") or [])
            lines.append(f"- {title} / {type_label} / {self._human_size(item.get('size'))} / {record_label} / 删除目标 {target_count}")
        if len(items) > 12:
            lines.append(f"... 另有 {len(items) - 12} 个媒体")
        lines.append("--------------------")
        if missing_count:
            lines.append("记录丢失条目需要在页面核对目录映射和源文件候选。")
        if link:
            lines.append("可点击下方按钮打开系统审核页面。")
        else:
            lines.append("未配置 MoviePilot 外部访问地址，无法生成审核跳转按钮。")
        self._post_cleanup_message(
            title="【媒体库管家】清理批次待确认",
            text="\n".join(lines),
            buttons=self._cleanup_batch_buttons(plan),
        )

    def _post_cleanup_message(self, title: str, text: str, buttons: Optional[List[List[Dict[str, str]]]] = None, **kwargs) -> None:
        link = self._cleanup_page_url()
        safe_buttons = self._cleanup_message_buttons(buttons)
        logger.info(
            "媒体库管家发送清理通知："
            f"title={title}，link={link or '-'}，buttons={sum(len(row) for row in safe_buttons or [])}，"
            f"parse_mode=HTML，mtype=default"
        )
        message_kwargs = {
            "title": title,
            "text": text,
            "buttons": safe_buttons or None,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            **kwargs,
        }
        if link:
            message_kwargs["link"] = link
        self.post_message(**message_kwargs)

    def _cleanup_batch_buttons(self, plan: Dict[str, Any]) -> List[List[Dict[str, str]]]:
        rows: List[List[Dict[str, str]]] = []
        link = self._cleanup_page_url()
        if link:
            rows.append([{"text": "打开清理计划", "url": link}])
        return rows

    def _cleanup_page_buttons(self) -> List[List[Dict[str, str]]]:
        link = self._cleanup_page_url()
        return [[{"text": "打开清理计划", "url": link}]] if link else []

    def _cleanup_page_url(self) -> str:
        link = self._clean_text(settings.MP_DOMAIN(f"#/plugin-app/{self.__class__.__name__}/main"))
        return link if self._is_http_url(link) else ""

    def _cleanup_message_buttons(self, buttons: Optional[List[List[Dict[str, str]]]]) -> List[List[Dict[str, str]]]:
        safe_rows: List[List[Dict[str, str]]] = []
        for row in buttons or []:
            safe_row = []
            for button in row or []:
                text = self._clean_text(button.get("text"))
                callback_data = self._clean_text(button.get("callback_data"))
                url = self._clean_text(button.get("url"))
                if not text:
                    continue
                if callback_data:
                    safe_row.append({"text": text, "callback_data": callback_data})
                elif self._is_http_url(url):
                    safe_row.append({"text": text, "url": url})
            if safe_row:
                safe_rows.append(safe_row)
        return safe_rows

    @staticmethod
    def _is_http_url(url: Any) -> bool:
        parsed = urlparse(str(url or "").strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

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

    def _load_cleanup_queue(self) -> List[Dict[str, Any]]:
        queue = self.get_data(self.DATA_KEY_CLEANUP_QUEUE) or []
        return queue if isinstance(queue, list) else []

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
            "library_synced_at": snapshot.get("library_synced_at"),
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
            "watched": len([item for item in media if item.get("watched")]),
            "watched_movies": len([item for item in movies if item.get("watched")]),
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
        return sorted(recommendations, key=lambda item: (item.get("watched") is False, -(int(item.get("size") or 0)), item.get("added_at") or ""))

    def _disk_status(self, snapshot: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        disks = self._media_disks(snapshot)
        status = []
        for disk in disks:
            path = disk["path"]
            if disk.get("unavailable"):
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
                        "warning": True,
                        "unavailable": True,
                        "error": disk.get("error") or "路径在 MoviePilot 容器内不可访问",
                    }
                )
                continue
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
            item["root_directories"] = self._media_root_directories(item)
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

    def _media_root_directories(self, item: Dict[str, Any]) -> List[Dict[str, str]]:
        result: List[Dict[str, str]] = []
        seen = set()
        for path in self._media_volume_paths(item):
            root_path = self._media_root_path(path)
            if not root_path or root_path in seen:
                continue
            seen.add(root_path)
            result.append({
                "path": root_path,
                "name": self._mount_name(root_path),
            })
        return result

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
            disk = self._unavailable_disk_identity(path)
            if not disk:
                return {}
            key = disk.get("key")
            if key not in cache:
                cache[key] = {
                    **disk,
                    "total": 0,
                    "free": 0,
                    "free_percent": 0,
                    "warning": True,
                }
            return cache[key]
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
        for library in snapshot.get("libraries", []):
            if library.get("path"):
                paths.append(library.get("path"))
            paths.extend(library.get("paths") or [])
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
                disk = self._unavailable_disk_identity(path)
                if not disk:
                    continue
                key = disk["key"]
                if key not in disks:
                    disks[key] = {**disk, "source_paths": []}
                disks[key]["source_paths"].append(self._path_preview(path))
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
            if str(parent) == current.anchor:
                break
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
            "key": mount_point,
            "path": mount_point,
            "mount_point": mount_point,
            "device": device,
            "display_name": self._volume_display_name(mount_point, device),
        }

    def _unavailable_disk_identity(self, path: Any) -> Dict[str, Any]:
        mount_point = self._media_root_path(path)
        if not mount_point:
            return {}
        return {
            "key": f"unavailable:{mount_point}",
            "path": mount_point,
            "mount_point": mount_point,
            "device": "",
            "display_name": self._mount_name(mount_point),
            "unavailable": True,
            "error": "路径在 MoviePilot 容器内不可访问",
        }

    def _media_root_path(self, path: Any) -> str:
        text = self._clean_text(path)
        if not text:
            return ""
        current = Path(text)
        if os.name == "nt":
            anchor = Path(current.anchor)
            parts = current.parts
            return str(anchor / parts[1]) if current.anchor and len(parts) > 1 else str(anchor or current)
        parts = current.parts
        if current.is_absolute() and len(parts) > 1:
            return "/" + parts[1]
        return parts[0] if parts else text

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

    def _capabilities(self) -> Dict[str, Any]:
        ai_agent_ready, ai_agent_message = self._ai_agent_status()
        return {
            "emby_scan": True,
            "transfer_history_match": True,
            "storage_delete": True,
            "ai_suggestions": True,
            "ai_agent_ready": ai_agent_ready,
            "ai_agent_message": ai_agent_message,
            "notification": True,
        }

    def _ai_resource_recognition_enabled(self) -> bool:
        ai_agent_ready, _ = self._ai_agent_status()
        return bool(self._config.get("ai_suggestions") and ai_agent_ready)

    @staticmethod
    def _ai_agent_status() -> Tuple[bool, str]:
        if not getattr(settings, "AI_AGENT_ENABLE", False):
            return False, "未配置智能助手，请先在系统设置中启用智能助手。"
        provider = str(getattr(settings, "LLM_PROVIDER", "") or "").strip().lower()
        model = str(getattr(settings, "LLM_MODEL", "") or "").strip()
        if not provider or not model:
            return False, "未配置智能助手，请先配置 LLM 提供商和模型。"
        api_key = str(getattr(settings, "LLM_API_KEY", "") or "").strip()
        if provider not in {"chatgpt", "github-copilot"} and not api_key:
            return False, "未配置智能助手，请先配置 LLM API Key。"
        return True, "智能助手已配置。"

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
        return f"清理计划存在 {blocked} 个记录丢失条目，请展开明细核对。"

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
