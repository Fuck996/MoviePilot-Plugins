from typing import Optional, Type

from app.agent.tools.base import MoviePilotTool
from pydantic import BaseModel, Field

from . import get_medialibrarykeeper_plugin


class SeedReviewInput(BaseModel):
    query: Optional[str] = Field(default=None, description="排查说明，可为空。")
    limit: int = Field(default=20, ge=1, le=100, description="最多返回的候选数量。")


class MediaLibraryKeeperSeedReviewTool(MoviePilotTool):
    name: str = "medialibrarykeeper_seed_review"
    description: str = (
        "读取媒体库管家当前清理批次中的缺 Hash 保种排查候选。"
        "当整理记录丢失或没有 download hash 时，插件会根据 MoviePilot 资源目录和下载器目录映射生成候选源文件、下载器路径，"
        "本工具用于给 AI 智能体提供判断上下文；工具只读，不会删除下载任务或媒体文件。"
    )
    args_schema: Type[BaseModel] = SeedReviewInput

    def get_tool_message(self, **kwargs) -> Optional[str]:
        return "正在读取媒体库管家的缺 Hash 保种排查候选。"

    async def run(self, query: Optional[str] = None, limit: int = 20, **kwargs) -> str:
        plugin = get_medialibrarykeeper_plugin()
        if not plugin:
            return "媒体库管家插件实例未初始化，暂时无法读取保种排查候选。"

        context = plugin.get_seed_review_context(limit=limit)
        candidates = context.get("candidates") or []
        if not candidates:
            return "当前清理批次没有缺 Hash 的保种排查候选。"

        lines = [
            f"清理计划：{context.get('plan_id') or '-'}",
            f"候选数量：{context.get('candidate_count')}",
            "请根据标题、源文件路径和下载器路径判断可能对应的下载任务，最终仍需要用户在界面确认。",
        ]
        if query:
            lines.append(f"排查说明：{query}")
        for index, candidate in enumerate(candidates, 1):
            lines.extend([
                "",
                f"{index}. {candidate.get('title') or '-'}（{candidate.get('type_label') or '-'}）",
                f"下载器：{candidate.get('downloader') or '-'}",
                f"下载器路径：{candidate.get('downloader_path') or '-'}",
                f"MP 资源路径：{candidate.get('source_path') or '-'}",
                f"状态：{candidate.get('status') or '-'}",
            ])
        return "\n".join(lines)
