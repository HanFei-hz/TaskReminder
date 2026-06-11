"""任务扫描器 — 从 tasks/task_NNN.md 读取任务并计算紧迫度。"""

import yaml
from datetime import date, datetime
from pathlib import Path
from typing import Any

# ============================================================
# [部署时修改] 指向你的 tasks/ 目录
# ============================================================
TASKS_DIR = Path("/your/project/tasks")


def parse_task_file(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        fm = yaml.safe_load(parts[1])
    except Exception:
        return None
    if not isinstance(fm, dict):
        return None
    body = parts[2].strip()

    deadline = None
    dl_raw = fm.get("deadline", "")
    if dl_raw:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m-%d", "%m/%d"):
            try:
                parsed = datetime.strptime(str(dl_raw), fmt).date()
                if fmt in ("%m-%d", "%m/%d"):
                    parsed = parsed.replace(year=date.today().year)
                deadline = parsed
                break
            except ValueError:
                continue

    return {
        "id": str(fm.get("id", path.stem.replace("task_", ""))),
        "title": str(fm.get("title", path.stem)),
        "project": str(fm.get("project", "")),
        "status": str(fm.get("status", "sleeping")),
        "priority": str(fm.get("priority", "P3")),
        "deadline": deadline,
        "body": body,
    }


def scan_tasks() -> list[dict[str, Any]]:
    """扫描 tasks/ 目录，返回所有活跃任务。"""
    tasks = []
    for fp in sorted(TASKS_DIR.glob("task_*.md")):
        t = parse_task_file(fp)
        if t and t["status"] != "archived":
            tasks.append(t)
    return tasks


def compute_urgency(task: dict[str, Any]) -> str:
    """计算任务紧迫度: high / medium / low。

    规则:
      - high: P1 且已过期，或 P1 且 deadline 在 15 天内
      - medium: P2 且 deadline 在 7 天内，或 P1 无 deadline
      - low: 其余
    """
    pri = task["priority"]
    dl = task["deadline"]
    today = date.today()

    if pri == "P1":
        if dl:
            days = (dl - today).days
            if days <= 0:
                return "high"
            if days <= 15:
                return "high"
        return "medium"

    if pri == "P2":
        if dl:
            days = (dl - today).days
            if days <= 0:
                return "high"
            if days <= 7:
                return "medium"
        return "medium"

    return "low"


def group_by_urgency(tasks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """按紧迫度分组。"""
    groups = {"high": [], "medium": [], "low": []}
    for t in tasks:
        u = compute_urgency(t)
        groups.setdefault(u, [])
        groups[u].append(t)
    return groups
