---
name: session-handoff
description: Resume checklist and recent repo state for future agents working in hora-finance.
---

# Session Handoff

Use this skill when resuming work after context loss.

## Current Shipped Behavior

- Commit `bf8b0be` added Google Sheets report generation on `main`.
- GitHub issue `#1` (`Boardroom`) was closed on 2026-03-15 after verifying that shipped code.
- Current user-facing commands are `python -m hora_finance`, `python -m hora_finance check`, and `python -m hora_finance report ...`.

## Resume Checklist

- Read `docs/agent-resume.md` first.
- Check `git status --short` for local-only or untracked artifacts before editing.
- Confirm whether the task needs live Google auth or can stay fully local and static.
- If workflow or architecture changes, update the relevant skills in the same commit.

## Known Gaps

- No automated tests are committed yet; prefer at least `pytest` and `python -m hora_finance check` when the environment allows.
