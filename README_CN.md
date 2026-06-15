# TaskReminder

把待办事项写进 Markdown 文件，每天早上自动收到一封任务日报邮件。

你只需要维护几个简单的 `.md` 文件，工具会自动按优先级和截止日期分三档（紧急/提醒/一般），组装成 HTML 邮件发到邮箱。适合同时推进多条研究线、一堆 deadline 怕漏掉的人。

纯 Python，仅需 PyYAML。独立模块，不绑定任何 AI 工具或框架。既可以配合 Claude Code 等 AI 助手对话式管理任务，也可以脱离 AI 作为纯命令行工具独立运行。

英文版见 [README.md](README.md)。

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

首次设置的详细步骤见 **[部署流程](部署流程.md)**（中文）或 **[DEPLOYMENT.md](DEPLOYMENT.md)**（英文）。

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
📋 任务日报 — 2026-06-12
6 个活跃任务

📌 本周重点
[你写在 phd_framework.md 里的本周计划]

🔴 紧急 (2)
┌────────┬──────────────────────┬───────┐
│ P1     │ 子刊 — 整机仿生推进   │ 剩60天 │
│        │ 更新补充说明中...     │       │
├────────┼──────────────────────┼───────┤
│ P2     │ 中期答辩 PPT         │ 已逾期 │
└────────┴──────────────────────┴───────┘
🟡 提醒 (3)
⚪ 一般 (1)
```

## 使用方式

TaskReminder 的使用分成两个阶段：**任务定制（冷启动）** 和 **任务部署（日常更新）**。工作流完全不同。

### 阶段一：任务定制（从零开始，只做一次）

这个阶段的核心是把你的研究规划"翻译"成一堆 `task_NNN.md` 文件。工具本身不帮你生成任务 — 你需要手写或借助 AI agent 来写。

**步骤：**

1. **梳理全局规划** — 创建 `phd_framework.md`，想清楚：
   - 你有几条研究线
   - 每条的目标期刊 / 截稿日期
   - 关键时间节点（答辩、回国、毕业盲审等）
   - 本周优先推什么（写入 `## 本周重点计划`）

2. **为每条研究线建 task 文件** — 在 `tasks/` 下创建 `task_001.md` ~ `task_NNN.md`，每个文件包含：
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
   - 待开始，文献调研阶段
   ## 下一步
   - [ ] 阅读相关论文，整理方法对比表
   ```
   - 此时"当前状态"可能还不具体 — 没关系，后续日常更新会逐步细化
   - 不确定截止日期可以先不填，填错的后面在文件里改即可

3. **首封邮件验证** — 运行 `python reminder.py --send`，检查：
   - 所有任务都出现在邮件里了吗
   - 紧迫度分级合理吗（阈值不对去改 `task_scanner.py`）
   - 本周重点区块正确显示了吗

4. **设置定时调度** — 把 cron / Task Scheduler 配好，**每周一**早 8 点自动发。之后就再也不用管定时器了。

> **推荐**：这一步在 Claude Code 里配合 agent 做，说一句"帮我搭建博士任务框架"就能一次生成所有文件。详见 [skill.md](skill.md)。

### 阶段二：任务部署（日常，反复做）

任务文件都建好之后，你的日常工作就很简单了：

- **改了东西** → 编辑对应 task 文件，改 `## 当前状态` 和 `## 下一步`；如果通过 AI agent 修改，邮件即时发送
- **每周一** → 定时兜底发送，同时更新 `phd_framework.md` 的 `## 本周重点计划`
- **新增论文线 / 子任务** → 新建一个 `task_NNN.md`，立即触发邮件
- **论文投出去了 / 任务完结** → frontmatter 改 `status: archived`，不再出现在邮件里
- **截止日期变了** → 改 frontmatter 的 `deadline` 字段，紧迫度自动重新算

两层发送机制：**每次变动立即发**（agent 修改任意文件后即时发送）+ **每周一早 8 点兜底**（cron 保底，确保即使一周没通过 agent 更新也能收到）。

## 定时发送

```bash
# Linux/macOS cron: 每周一早 8 点（兜底）
0 8 * * 1 cd /path/to/TaskReminder && python reminder.py --send

# Windows Task Scheduler: 每周一
schtasks /Create /TN "TaskReminder" /TR "python X:\path\to\reminder.py --send" /SC WEEKLY /D MON /ST 08:00
```

如果配合 AI agent 使用，每次任务变动也会即时发送，不需要等到周一。

## 文件结构

```
TaskReminder/
├── task_scanner.py        扫描器：解析任务 + 计算紧迫度
├── reminder.py            CLI 入口：组稿 HTML → 发送
├── email_client.py        SMTP SSL 发送封装
├── phd_framework.md       全局规划（本周重点 + 论文版图 + 关键节点）
├── config.template.json   SMTP 配置模板
├── skill.md               AI agent 工作流说明（英文）
├── skill_CN.md            AI agent 工作流说明（中文）
├── DEPLOYMENT.md          详细部署指南（英文）
├── 部署流程.md              详细部署指南（中文）
├── README.md              本文件（中文）
└── README.md              英文 README
```

## 依赖

- Python 3.9+
- PyYAML ≥ 6.0

## 许可

MIT
