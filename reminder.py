#!/usr/bin/env python3
"""任务提醒 CLI — 扫描任务 → 组稿 → 邮件发送。

用法:
    python reminder.py                    # 扫描并打印概要
    python reminder.py --send             # 扫描并发送邮件
    python reminder.py --to user@qq.com   # 指定收件地址

可通过 cron / Task Scheduler 定时调用。
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from task_scanner import scan_tasks, group_by_urgency
from email_client import send_email, load_config


# ============================================================
# [部署时修改] 指向你的 phd_framework.md（可选，没有则跳过）
# ============================================================
FRAMEWORK_PATH = Path(__file__).parent / "phd_framework.md"


def read_weekly_plan() -> str:
    """从 phd_framework.md 读取「本周重点计划」区块。"""
    if not FRAMEWORK_PATH.exists():
        return ""
    text = FRAMEWORK_PATH.read_text(encoding="utf-8")
    m = re.search(r"## 本周重点计划\n\n([\s\S]*?)(?=\n## )", text)
    if not m:
        return ""
    return m.group(1).strip()


URGENCY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "⚪"}
URGENCY_LABEL = {"high": "紧急", "medium": "提醒", "low": "一般"}


def fmt_deadline(task) -> str:
    dl = task.get("deadline")
    if not dl:
        return ""
    days = (dl - date.today()).days
    if days < 0:
        return f"（已逾期 {abs(days)} 天）"
    if days == 0:
        return "（今天到期）"
    return f"（剩 {days} 天）"


try:
    "\U0001f4cb".encode(sys.stdout.encoding or "utf-8")
except (UnicodeEncodeError, UnicodeDecodeError):
    pass


_TAG = {"high": "[!]", "medium": "[*]", "low": "[-]"}


def build_report(tasks: list[dict]) -> str:
    """构建纯文本报告。"""
    groups = group_by_urgency(tasks)
    tag = _TAG
    lines = [
        f"任务日报 — {date.today().isoformat()}",
        f"总计 {len(tasks)} 个活跃任务",
        "",
    ]

    for key in ("high", "medium", "low"):
        group = groups.get(key, [])
        if not group:
            continue
        label = URGENCY_LABEL[key]
        lines.append(f"--- {tag[key]} {label} ({len(group)}) ---")
        for t in sorted(group, key=lambda x: x.get("deadline") or date.max):
            dl_str = fmt_deadline(t)
            lines.append(f"  [{t['priority']}] {t['title']} {dl_str}")
            if t["project"]:
                lines.append(f"       项目: {t['project']}")
        lines.append("")

    return "\n".join(lines)


def _extract_sections(body: str) -> tuple[str, str]:
    """从任务 body 中提取「当前状态」和「下一步」。"""
    status = ""
    next_steps = ""
    m = re.search(r"## 当前状态\n+([\s\S]*?)(?=\n## |$)", body)
    if m:
        status = m.group(1).strip()
    m = re.search(r"## 下一步\n+([\s\S]*?)(?=\n## |$)", body)
    if m:
        next_steps = m.group(1).strip()
    return status, next_steps


def build_html(tasks: list[dict]) -> str:
    """构建 HTML 邮件正文。"""
    groups = group_by_urgency(tasks)
    weekly = read_weekly_plan().replace("\n", "<br>")

    def section(key: str) -> str:
        group = groups.get(key, [])
        if not group:
            return ""
        emoji = URGENCY_EMOJI[key]
        label = URGENCY_LABEL[key]
        rows = "\n".join(
            f"<tr>"
            f"<td style='padding:6px 12px;border:1px solid #ddd;'>{t['priority']}</td>"
            f"<td style='padding:6px 12px;border:1px solid #ddd;'>"
            f"<strong>{t['title']}</strong>"
            f"{_format_body_block(t.get('body',''))}"
            f"</td>"
            f"<td style='padding:6px 12px;border:1px solid #ddd;'>{t.get('project','')}</td>"
            f"<td style='padding:6px 12px;border:1px solid #ddd;'>{fmt_deadline(t)}</td>"
            f"</tr>"
            for t in sorted(group, key=lambda x: x.get("deadline") or date.max)
        )
        color = {"high": "#e74c3c", "medium": "#f39c12", "low": "#95a5a6"}[key]
        return f"""
<h3 style='color:{color};'>{emoji} {label}</h3>
<table style='border-collapse:collapse;width:100%;max-width:650px;margin-bottom:20px;'>
<tr style='background:#f5f5f5;'>
<th style='padding:6px 12px;border:1px solid #ddd;text-align:left;'>优先级</th>
<th style='padding:6px 12px;border:1px solid #ddd;text-align:left;'>任务 & 进度</th>
<th style='padding:6px 12px;border:1px solid #ddd;text-align:left;'>项目</th>
<th style='padding:6px 12px;border:1px solid #ddd;text-align:left;'>截止</th>
</tr>
{rows}
</table>"""

    return f"""<html><body style='font-family:"Segoe UI",Arial,sans-serif;padding:20px;'>
<h2>📋 任务日报</h2>
<p style='color:#666;'>{date.today().isoformat()} — {len(tasks)} 个活跃任务</p>
<div style='background:#f0f7ff;border-left:4px solid #3498db;padding:12px 16px;margin:16px 0;border-radius:0 4px 4px 0;'>
<h3 style='margin:0 0 8px 0;color:#2c3e50;'>📌 本周重点</h3>
<p style='margin:0;line-height:1.6;color:#444;'>{weekly}</p>
</div>
{section('high')}
{section('medium')}
{section('low')}
<p style='color:#999;font-size:12px;margin-top:30px;'>— TaskReminder 自动生成</p>
</body></html>"""


def _format_body_block(body: str) -> str:
    """格式化任务 body 中的状态和下一步为 HTML 片段。"""
    if not body:
        return ""
    status, next_steps = _extract_sections(body)
    parts = []
    if status:
        parts.append(
            f"<div style='font-size:12px;color:#555;margin-top:4px;line-height:1.5;'>"
            f"{status.replace(chr(10), '<br>')}"
            f"</div>"
        )
    if next_steps:
        parts.append(
            f"<div style='font-size:12px;color:#888;margin-top:2px;line-height:1.5;'>"
            f"{next_steps.replace(chr(10), '<br>')}"
            f"</div>"
        )
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description="TaskReminder 任务提醒")
    parser.add_argument("--send", action="store_true", help="发送邮件")
    parser.add_argument("--to", default=None, help="收件地址（默认用 config.json 的 to_addr）")
    args = parser.parse_args()

    tasks = scan_tasks()
    if not tasks:
        print("没有活跃任务。")
        return

    if args.send:
        html = build_html(tasks)
        config = load_config()
        to_addr = args.to or (getattr(config, "to_addr", "") if config else "")
        if not to_addr:
            print("[reminder] 未指定收件地址，使用 --to 或在 config.json 设置 to_addr")
            print(build_report(tasks))
            return
        ok = send_email(to_addr, f"📋 任务日报 {date.today().isoformat()}", html)
        if ok:
            print("[reminder] 邮件已发送")
        else:
            print("[reminder] 邮件发送失败", file=__import__("sys").stderr)
    else:
        print(build_report(tasks))


if __name__ == "__main__":
    main()
