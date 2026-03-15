---
name: repo-map
description: Fast map of the hora-finance codebase and where to make changes.
---

# Repo Map

Use this skill to choose the right file before editing.

## Entry Points

- `src/hora_finance/__main__.py`: CLI commands `serve`, `check`, and `report`.
- `src/hora_finance/app.py`: Flask routes for auth, health, user info, and `/reports/google-sheet`.

## Core Modules

- `src/hora_finance/config.py`: env vars, data dir, reports dir, and client secret path.
- `src/hora_finance/google_auth.py`: desktop OAuth flow and required Google scopes.
- `src/hora_finance/storage.py`: SQLite schema, active session, and credential persistence.
- `src/hora_finance/sheets.py`: Sheets API fetch and scope validation.
- `src/hora_finance/reporting.py`: row parsing, aggregation, and markdown report generation.

## Operator Docs

- `README.md`: local setup and runtime commands.
- `docs/agent-resume.md`: current state, recent history, and resume checklist.
