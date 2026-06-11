# TaskReminder

每日任务扫描 + 紧迫度分级 + HTML 邮件提醒。为**同时推进多条研究线 + 有硬 deadline** 的场景设计。

纯 Python，仅需 PyYAML。独立模块，不绑定任何框架。

## 场景：为什么需要它？

当你同时跟 5-6 条研究线，每条有不同的阶段和截止日期，每天打开电脑需要一眼知道 **今天该优先推什么**、**哪个快过期了**。

TaskReminder 做的事情：

1. 扫描你手写的 `task_NNN.md` 任务文件（Markdown + YAML frontmatter）
2. 根据优先级和截止日期自动分三档：🔴 紧急 / 🟡 提醒 / ⚪ 一般
3. 组装 HTML 邮件 — 每个任务行内嵌当前状态和下一步，顶部显示本周重点
4. 每天早上定时发送到邮箱，手机/电脑打开就能看到

不需要数据库，不需要 Web 服务，任务就是 Markdown 文件，随时改、随时生效。

## 快速开始

```bash
git clone git@github.com:HanFei-hz/TaskReminder.git
cd TaskReminder
pip install pyyaml

# 1. 配置 SMTP
cp config.template.json config.json
# 编辑 config.json，填入你的邮箱和 SMTP 授权码

# 2. 修改任务目录路径
# 打开 task_scanner.py，将 TASKS_DIR 改为你的 tasks/ 目录

# 3. 终端预览
python reminder.py

# 4. 发送邮件
python reminder.py --send
```

首次设置的详细步骤见 **[部署流程](部署流程.md)**。

## 任务文件格式

在 `tasks/` 目录下创建 `task_NNN.md`，格式如下：

```markdown
---
id: "001"
title: 子刊 — 整机仿生推进
project: 论文
status: active
priority: P1
deadline: "2026-08-15"
---

## 当前状态
- 更新补充说明中
- 算法命名待统一

## 下一步
- [ ] 与导师确认引言和讨论
- [ ] 替换 DRL 表述、检查图表说明
```

- `status: active` 才会被扫描，设为 `archived` 自动跳过
- `deadline` 不填则无截止提醒，仅按优先级分级
- `## 当前状态` 和 `## 下一步` 会嵌入邮件正文

## 紧迫度规则

| 条件 | 等级 |
|------|------|
| P1 已过期，或 P1 15 天内到期 | 🔴 紧急 |
| P2 已过期，或 P2 7 天内到期 | 🟡 提醒 |
| P1 无 deadline / 其余情况 | ⚪ 一般 |

阈值可在 `task_scanner.py` 的 `compute_urgency()` 中调整。

## 邮件效果

每天早上 8 点的邮件长这样：

```
📋 任务日报 — 2026-06-11
6 个活跃任务

📌 本周重点
[你写在 phd_framework.md 里的本周计划]

🔴 紧急 (2)
┌────────┬──────────────────────┬───────┐
│ P1    │ 子刊 — 整机仿生推进    │ 剩60天 │
│       │ 更新补充说明中...      │       │
├────────┼──────────────────────┼───────┤
│ P2    │ 中期答辩 PPT          │ 已逾期 │
└────────┴──────────────────────┴───────┘
🟡 提醒 (3)
⚪ 一般 (1)
```

## 日常使用

### 初始化（第一次）

1. 建立 `phd_framework.md`（全局规划文件），写好论文版图和本周重点
2. 为每条研究线创建 `task_NNN.md`，填好 frontmatter 和当前状态
3. 设置定时调度（cron / Task Scheduler），每天早 8 点自动发送
4. 跑一次 `python reminder.py --send` 确认能收到邮件

### 日常更新

- **推进研究后** — 编辑对应 `task_NNN.md` 的 `## 当前状态` 和 `## 下一步`
- **每周规划** — 更新 `phd_framework.md` 的 `## 本周重点计划`，周一早上的邮件自动体现
- **新增任务** — 新建 `task_NNN.md`，按模板填好，明天起自动出现在邮件里
- **完成任务归档** — frontmatter 改 `status: archived`，不再出现在邮件中

### 配合 Claude Code（可选）

在 Claude Code 环境里配置 agent 技能，说"提醒"即可自动执行扫描→同步进度→发送。详见 [skill.md](skill.md)。

## 定时发送

```bash
# Linux/macOS cron: 每天早 8 点
0 8 * * * cd /path/to/TaskReminder && python reminder.py --send

# Windows Task Scheduler
schtasks /Create /TN "TaskReminder" /TR "python X:\path\to\reminder.py --send" /SC DAILY /ST 08:00
```

## 文件结构

```
TaskReminder/
├── task_scanner.py        扫描器：解析任务 + 计算紧迫度
├── reminder.py            CLI 入口：组稿 HTML → 发送
├── email_client.py        SMTP SSL 发送封装
├── phd_framework.md       全局规划（本周重点 + 论文版图 + 关键节点）
├── config.template.json   SMTP 配置模板
├── skill.md               Claude Code agent 工作流说明
├── 部署流程.md             详细部署指南（首次使用必读）
└── README.md              本文件
```

## 依赖

- Python 3.9+
- PyYAML ≥ 6.0

## 许可

MIT
