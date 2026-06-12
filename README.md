# TaskReminder

Write your todos in Markdown files. Get a daily task digest email every morning. No database, no web service.

You maintain a handful of `.md` files. The tool scans them, sorts tasks by urgency (critical / warning / normal), and sends a formatted HTML email. Built for people juggling multiple research threads and too many deadlines.

Pure Python, only requires PyYAML. Works standalone as a CLI tool — no AI assistant required. Also pairs well with AI coding agents (Claude Code, Cursor, etc.) for conversational task management.

For Chinese docs, see [README_CN.md](README_CN.md) and [部署流程.md](部署流程.md).

## Why?

When you're running 5-6 research threads, each with different stages and deadlines, you need to know at a glance: what to push today, and what's about to slip.

TaskReminder does exactly that:

1. Scans your `task_NNN.md` files (Markdown + YAML frontmatter)
2. Ranks every task by priority and deadline into three tiers: 🔴 critical / 🟡 warning / ⚪ normal
3. Builds an HTML email — each task row shows current status and next steps, with this week's priorities at the top
4. Delivers it to your inbox every morning, readable on phone or desktop

## Quick Start

```bash
git clone git@github.com:HanFei-hz/TaskReminder.git
cd TaskReminder
pip install pyyaml

# 1. Configure SMTP
cp config.template.json config.json
# Edit config.json with your email and SMTP app password

# 2. Point to your tasks directory
# Open task_scanner.py, set TASKS_DIR to your tasks/ folder

# 3. Preview in terminal
python reminder.py

# 4. Send the email
python reminder.py --send
```

For detailed setup instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Task File Format

Create `task_NNN.md` files in your `tasks/` directory:

```markdown
---
id: "001"
title: Sub-journal — Bio-inspired propulsion
project: Paper
status: active
priority: P1
deadline: "2026-08-15"
---

## Current Status
- Updating supplementary notes
- Algorithm naming needs unification

## Next Steps
- [ ] Confirm intro and discussion with advisor
- [ ] Replace DRL terminology, review figure captions
```

- `status: active` is scanned; `archived` tasks are skipped automatically
- Leave `deadline` empty if there's no hard cutoff
- `## Current Status` and `## Next Steps` are embedded in the email body

## Urgency Rules

| Condition | Level |
|-----------|-------|
| P1 overdue, or P1 within 15 days | 🔴 Critical |
| P2 overdue, or P2 within 7 days | 🟡 Warning |
| P1 no deadline / everything else | ⚪ Normal |

Thresholds can be adjusted in `task_scanner.py` → `compute_urgency()`.

## What the Email Looks Like

```
📋 Task Digest — 2026-06-12
6 active tasks

📌 This Week's Focus
[Your weekly plan, read from phd_framework.md]

🔴 Critical (2)
┌────────┬──────────────────────────┬───────────┐
│ P1     │ Sub-journal — Bio-imitation│ 60 days left │
│        │ Updating notes...        │           │
├────────┼──────────────────────────┼───────────┤
│ P2     │ Mid-term defense PPT     │ Overdue   │
└────────┴──────────────────────────┴───────────┘
🟡 Warning (3)
⚪ Normal (1)
```

## Usage Workflow

There are two distinct phases: **Task Bootstrapping** (one-time setup) and **Task Maintenance** (daily use).

### Phase 1: Bootstrapping

Translate your research plan into `task_NNN.md` files. The tool doesn't generate tasks for you — you write them, or use an AI agent to help.

**Steps:**

1. **Create `phd_framework.md`** — your master plan:
   - How many research threads
   - Target journal / deadline for each
   - Key milestones (defense, submission, graduation, etc.)
   - This week's priorities (under `## This Week's Focus`)

2. **Create task files** — `task_001.md` through `task_NNN.md` in your `tasks/` directory:
   ```markdown
   ---
   id: "001"
   title: Sub-journal — Bio-inspired propulsion
   project: Paper
   status: active
   priority: P1
   deadline: "2026-08-15"
   ---
   ## Current Status
   - Starting out, literature survey phase
   ## Next Steps
   - [ ] Read relevant papers, compile comparison table
   ```
   - "Current Status" can be vague at first — you'll refine it over time
   - Leave `deadline` blank if unsure; fix it in the file later

3. **Send the first email** — run `python reminder.py --send` and check:
   - All tasks appear in the email
   - Urgency levels make sense (adjust thresholds in code if needed)
   - Weekly focus section shows correctly

4. **Schedule daily delivery** — set up cron or Task Scheduler for 8 AM. Never touch the timer again.

> **Tip**: Use an AI agent (Claude Code, Cursor, etc.) to bootstrap — "build my PhD task framework" generates all files in one go. See [skill.md](skill.md).

### Phase 2: Daily Maintenance

Once tasks are set up, your day-to-day is minimal:

- **Made progress** → edit the task file's `## Current Status` and `## Next Steps`
- **Every Monday** → update `## This Week's Focus` in `phd_framework.md`; tomorrow's email reflects it
- **New thread / subtask** → create a new `task_NNN.md`; appears in tomorrow's email
- **Paper submitted / task done** → change frontmatter to `status: archived`; gone from the email
- **Deadline changed** → update the `deadline` field; urgency recalculated automatically

Zero code changes — just edit Markdown files. The email lands at 8 AM every day.

## Scheduling

```bash
# Linux/macOS cron: daily at 8 AM
0 8 * * * cd /path/to/TaskReminder && python reminder.py --send

# Windows Task Scheduler
schtasks /Create /TN "TaskReminder" /TR "python X:\path\to\reminder.py --send" /SC DAILY /ST 08:00
```

## File Structure

```
TaskReminder/
├── task_scanner.py        Scanner: parse tasks + compute urgency
├── reminder.py            CLI entry: build HTML → send
├── email_client.py        SMTP SSL sender
├── phd_framework.md       Master plan (weekly focus + paper roadmap + milestones)
├── config.template.json   SMTP config template
├── skill.md               AI agent workflow guide
├── DEPLOYMENT.md          Detailed setup guide (English)
├── 部署流程.md              Detailed setup guide (Chinese)
├── README.md              This file (English)
└── README_CN.md           Chinese README
```

## Dependencies

- Python 3.9+
- PyYAML >= 6.0

## License

MIT
