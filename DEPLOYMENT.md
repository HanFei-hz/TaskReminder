# TaskReminder Deployment Guide

> Daily task scanner + urgency ranking + HTML email digest. Pure Python, only needs PyYAML.

## 1. System Overview

```
tasks/task_001.md   --+
tasks/task_002.md   --+  task_scanner.py     reminder.py      email_client.py
    ...              +-- parse frontmatter --+ build HTML ----+ SMTP send
tasks/task_NNN.md   --+  + compute urgency                     (QQ / 163 / Gmail)

phd_framework.md ----+ reminder.py reads "This Week's Focus" and embeds it at email top
```

## 2. Requirements

- Python 3.9+
- `pip install pyyaml`
- An email account with SMTP access (QQ, 163, Gmail, or any provider)

## 3. File Overview

| File | Purpose |
|------|---------|
| `task_scanner.py` | Scans `tasks/task_*.md`, parses frontmatter + computes urgency |
| `reminder.py` | CLI entry point, builds HTML, supports `--send` |
| `email_client.py` | SMTP SSL sender, reads config from `config.json` |
| `config.json` | SMTP credentials (gitignored) |
| `config.template.json` | Config template — copy and fill in |
| `phd_framework.md` | Optional. If present, "This Week's Focus" section is embedded at email top |

## 4. Required Changes

Before deploying, modify these locations across **3 files**:

### 4.1 `task_scanner.py`

| Variable | Change to |
|----------|-----------|
| `TASKS_DIR` | Absolute path to your `tasks/` directory |

```python
TASKS_DIR = Path("/your/project/tasks")
```

### 4.2 `reminder.py`

| Variable | Change to |
|----------|-----------|
| `FRAMEWORK_PATH` | Path to your `phd_framework.md` (ignore if not using) |

```python
FRAMEWORK_PATH = Path(__file__).parent / "phd_framework.md"
```

### 4.3 `email_client.py`

| Variable | Change to |
|----------|-----------|
| `CONFIG_PATH` | Path to your `config.json` (leave as default if in same directory) |

### 4.4 SMTP Config

```bash
cp config.template.json config.json
```

Edit `config.json`:
```json
{
    "host": "smtp.qq.com",
    "port": 465,
    "user": "your_email@qq.com",
    "password": "your-smtp-app-password",
    "to_addr": "recipient@example.com"
}
```

Common SMTP servers:
| Provider | Host | Port |
|----------|------|------|
| QQ Mail | smtp.qq.com | 465 |
| 163 Mail | smtp.163.com | 465 |
| Gmail | smtp.gmail.com | 465 |
| Outlook | smtp-mail.outlook.com | 587 |

## 5. Task File Format

Each task file is named `task_NNN.md` with YAML frontmatter:

```markdown
---
id: "001"
title: Your task title
project: Project name (optional)
status: active
priority: P1
deadline: "2026-08-15"
---

## Current Status
- What you're working on
- Progress made so far

## Next Steps
- [ ] Action item 1
- [ ] Action item 2
```

Fields:
| Field | Required | Notes |
|-------|----------|-------|
| id | Yes | Task identifier |
| title | Yes | Task name |
| project | No | Project name, hidden if empty |
| status | Yes | `active` (scanned) or `archived` (skipped) |
| priority | Yes | P1 / P2 / P3 |
| deadline | No | Format `YYYY-MM-DD`; no deadline reminder if omitted |
| body | Yes | `## Current Status` + `## Next Steps` — embedded in email |

## 6. Urgency Rules

| Condition | Level |
|-----------|-------|
| P1 overdue, or P1 within 15 days | 🔴 High |
| P2 overdue, or P2 within 7 days | 🟡 Medium |
| P1 no deadline, or P2 >7 days out | 🟡 Medium |
| Everything else | ⚪ Low |

Adjust thresholds in `task_scanner.py` → `compute_urgency()`.

## 7. Scheduling

### Windows (Task Scheduler)

```cmd
schtasks /Create /TN "TaskReminder" /TR "python X:\path\to\reminder.py --send" /SC DAILY /ST 08:00
```

### Linux / macOS (cron)

```bash
crontab -e
# Daily at 8 AM
0 8 * * * cd /path/to/TaskReminder && python reminder.py --send
```

### AI Agent Trigger

In Claude Code or similar: tell the agent "reminder" and it runs `python reminder.py --send`.

## 8. Testing

```bash
# Terminal preview (no email sent)
python reminder.py

# Send email
python reminder.py --send

# Send to a specific address (overrides config.json to_addr)
python reminder.py --send --to test@example.com
```

## 9. Customization

- **Email styling** — edit HTML/CSS in `reminder.py` → `build_html()`
- **Weekly focus section** — create `phd_framework.md` with a `## This Week's Focus` section; email reads it automatically
- **Urgency thresholds** — edit day counts in `task_scanner.py` → `compute_urgency()`

## 10. Dependencies

```
PyYAML>=6.0
```

Python stdlib: `smtplib`, `email`, `json`, `argparse`, `re`, `datetime`, `pathlib`, `dataclasses`
