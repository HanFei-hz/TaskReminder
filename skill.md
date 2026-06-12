# TaskReminder — Daily Task Reminder Skill

> Scan Markdown task files → urgency ranking → build HTML email → SMTP send.
> Standalone module, no framework or backend dependency.

## Triggers

- User says "reminder" / "daily digest" / "what's on my plate" / "send report"
- Scheduled daily auto-send via cron / Task Scheduler
- Agent runs `python reminder.py --send`

## Core Flow

```
1. task_scanner.py scans tasks/task_*.md
   +-- Parse YAML frontmatter (id, title, priority, deadline, project)
   +-- Extract ## Current Status and ## Next Steps from body
   +-- Compute urgency (high / medium / low)

2. reminder.py builds the email
   +-- Reads "This Week's Focus" from phd_framework.md (optional)
   +-- Groups tasks by urgency, builds HTML table
   +-- Each task row embeds status + next steps

3. email_client.py sends
   +-- SMTP SSL (default port 465)
   +-- Supports QQ / 163 / Gmail / any SMTP provider
```

## Agent Workflow

When user triggers a reminder or the daily schedule fires, the agent should:

1. **Scan tasks** — `python reminder.py` to preview terminal output, confirm active tasks
2. **Check weekly focus** — open `phd_framework.md`, verify `## This Week's Focus` is up to date
3. **Sync progress** — if user has verbally reported updates, sync to `task_NNN.md` before sending
4. **Send** — `python reminder.py --send`
5. **Report** — tell user whether the email was sent successfully

## Task File Template

```markdown
---
id: "NNN"
title: Task title
project: Project name (optional)
status: active
priority: P1
deadline: "2026-08-15"
---

## Objective
One-line goal description

## Current Status
- What you're working on
- Progress made

## Next Steps
- [ ] Action items
```

## Urgency Rules (adjustable in code)

| Condition | Level | Email display |
|-----------|-------|---------------|
| P1 overdue | 🔴 High | Red header |
| P1 within 15 days | 🔴 High | Red header |
| P2 overdue / within 7 days | 🟡 Medium | Orange header |
| Everything else | ⚪ Low | Gray header |

## Email Structure

```
+--------------------------------+
| +- Task Digest -- 2026-06-12   |
| 6 active tasks                  |
+----------------------------------+
| *- This Week's Focus             |
| [reads from phd_framework.md]   |
+----------------------------------+
| .. Critical (2)                  |
| +--------+-------------+-------+ |
| | Priority | Task & Progress | Due  | |
| | P1    | Title      | 60d left | |
| |       | Status...  |         | |
| |       | Next steps |         | |
| +--------+-------------+-------+ |
| | ...    | ...        | ...     | |
| +--------+-------------+-------+ |
+----------------------------------+
| .- Warning / .. Normal          |
| [same structure]                 |
+----------------------------------+
```

## Customizable Points

- **SMTP config** — `config.json`, any mail provider
- **Task path** — `task_scanner.py:8`, change `TASKS_DIR`
- **Urgency thresholds** — `task_scanner.py:compute_urgency()`, change day counts
- **Email styling** — `reminder.py:build_html()`, change HTML/CSS
- **Weekly focus source** — `reminder.py:read_weekly_plan()`, change regex or swap for API/database

## Notes

- Requires Python 3.9+ and `pyyaml`
- SMTP password must be an **app password**, not your login password (QQ Mail → Settings → Account → POP3/SMTP → Generate)
- Emoji rendering may fail on Windows Git Bash terminal; emojis are only used in the HTML email
- Port 465 uses SSL; for TLS use port 587 and change `smtplib.SMTP_SSL` → `smtplib.SMTP` + `starttls()`
