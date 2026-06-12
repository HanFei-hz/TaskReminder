# TaskReminder — 每日任务提醒 Skill

> 扫描 Markdown 任务文件 → 紧迫度分级 → 组装 HTML 邮件 → SMTP 发送。
> 独立模块，不绑定任何框架或后端。

英文版见 [skill.md](skill.md)。

## 触发条件

- 用户说"发提醒" / "发送日报" / "今天有什么任务" / "reminder"
- 每天早上定时自动发送（通过 cron / Task Scheduler）
- agent 执行 `python reminder.py --send`

## 核心流程

```
1. task_scanner.py 扫描 tasks/task_*.md
   └─ 解析 YAML frontmatter（id, title, priority, deadline, project）
   └─ 提取 body 中 ## 当前状态 和 ## 下一步 区块
   └─ 计算紧迫度（high / medium / low）

2. reminder.py 组稿
   └─ 读取 phd_framework.md 的「本周重点计划」（可选）
   └─ 按紧迫度分组，构建 HTML 表格
   └─ 每个任务行内嵌状态 + 下一步

3. email_client.py 发送
   └─ SMTP SSL（默认 465 端口）
   └─ 支持 QQ / 163 / Gmail
```

## agent 工作流

当用户说"提醒"或每天定时触发时，agent 应：

1. **扫描任务** — `python reminder.py` 先看终端输出，确认有活跃任务
2. **检查本周重点** — 打开 `phd_framework.md`，确认 `## 本周重点计划` 是否最新
3. **检查任务状态** — 如果用户口头更新过进度，先同步到 `task_NNN.md` 再发送
4. **发送** — `python reminder.py --send`
5. **报告结果** — 告知用户邮件是否发送成功

## 任务文件模板

```markdown
---
id: "NNN"
title: 任务标题
project: 所属项目（可选）
status: active
priority: P1
deadline: "2026-08-15"
---

## 目标
一句话描述目标

## 当前状态
- 正在做的事情
- 已完成的进展

## 下一步
- [ ] 待做事项
```

## 紧迫度规则（可在代码中调整）

| 条件 | 等级 | 邮件显示 |
|------|------|---------|
| P1 已过期 | 🔴 high | 红色标题 |
| P1 15天内到期 | 🔴 high | 红色标题 |
| P2 已过期 / 7天内到期 | 🟡 medium | 橙色标题 |
| 其余 | ⚪ low | 灰色标题 |

## 邮件结构

```
┌─────────────────────────────┐
│ 📋 任务日报 — 2026-06-12    │
│ 6 个活跃任务                │
├─────────────────────────────┤
│ 📌 本周重点                  │
│ [从 phd_framework.md 读取]  │
├─────────────────────────────┤
│ 🔴 紧急 (2)                 │
│ ┌──────┬──────────┬───────┐ │
│ │ 优先级│ 任务&进度 │ 截止  │ │
│ │ P1   │ 标题     │ 剩X天 │ │
│ │      │ 状态...  │       │ │
│ │      │ 下一步.. │       │ │
│ ├──────┼──────────┼───────┤ │
│ │ ...  │ ...     │ ...   │ │
│ └──────┴──────────┴───────┘ │
├─────────────────────────────┤
│ 🟡 提醒 / ⚪ 一般           │
│ [同上结构]                   │
└─────────────────────────────┘
```

## 可自定义项

- **SMTP 配置** — `config.json`，支持任意邮件服务商
- **任务路径** — `task_scanner.py:8`，改 `TASKS_DIR`
- **紧迫度阈值** — `task_scanner.py:compute_urgency()`，改天数
- **邮件样式** — `reminder.py:build_html()`，改 HTML/CSS
- **本周重点来源** — `reminder.py:read_weekly_plan()`，改正则或换成 API/数据库

## 注意事项

- 需 Python 3.9+ 和 `pyyaml`
- 邮箱 SMTP 密码是**授权码**，不是登录密码（QQ邮箱 → 设置 → 账户 → POP3/SMTP → 生成授权码）
- Windows Git Bash 下 emoji 可能乱码，只在 HTML 邮件中使用 emoji
- 端口 465 使用 SSL；如需 TLS 改用 587 并改 `smtplib.SMTP_SSL` → `smtplib.SMTP` + `starttls()`
