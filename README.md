# TaskReminder

每日任务扫描 + 紧迫度分级 + HTML 邮件提醒。纯 Python，仅需 PyYAML。

## 做什么

- 扫描 `tasks/task_*.md` 任务文件（YAML frontmatter）
- 按 P1/P2/P3 和截止日自动分级（紧急/提醒/一般）
- 组装 HTML 邮件，每个任务内嵌当前状态和下一步
- 通过 SMTP（QQ/163/Gmail）发送

## 快速开始

```bash
pip install pyyaml
cp config.template.json config.json   # 填入 SMTP 凭据
# 修改 task_scanner.py 的 TASKS_DIR 指向你的任务目录
python reminder.py                    # 终端预览
python reminder.py --send             # 发送邮件
```

## 定时发送

```bash
# Linux/macOS cron: 每天早 8 点
0 8 * * * cd /path/to/TaskReminder && python reminder.py --send

# Windows Task Scheduler
schtasks /Create /TN "TaskReminder" /TR "python X:\path\to\reminder.py --send" /SC DAILY /ST 08:00
```

## 任务文件格式

```markdown
---
id: "001"
title: 任务标题
project: 所属项目（可选）
status: active
priority: P1
deadline: "2026-08-15"
---

## 当前状态
- 正在做的事情

## 下一步
- [ ] 待做事项
```

## 目录结构

```
├── task_scanner.py      扫描器：解析任务 + 计算紧迫度
├── reminder.py          CLI 入口：组稿 HTML → 发送
├── email_client.py      SMTP SSL 发送封装
├── config.template.json SMTP 配置模板
├── skill.md             agent 工作流说明
└── 部署流程.md           详细部署指南
```

## 依赖

- Python 3.9+
- PyYAML ≥ 6.0
