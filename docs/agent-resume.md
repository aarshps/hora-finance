# Agent Resume

Updated: 2026-03-15

## Repo Purpose

- Local-only personal finance app built with Flask, SQLite, and Google OAuth.
- Google Sheets data can be turned into markdown finance reports by CLI or HTTP.

## Entry Points

- `python -m hora_finance`: starts the local app on `127.0.0.1:8765`.
- `python -m hora_finance check`: initializes storage and prints resolved config paths.
- `python -m hora_finance report --spreadsheet-id "<id>" [--range ...] [--output ...]`: fetches a sheet and saves a markdown report.

## Runtime Paths

- Data dir: `HORA_FINANCE_DATA_DIR` or `~/.hora-finance`
- SQLite DB: `<data dir>/hora_finance.db`
- Reports dir: `HORA_FINANCE_REPORTS_DIR` or `<data dir>/reports`
- Google client secret: `HORA_FINANCE_GOOGLE_CLIENT_SECRET` or `<data dir>/google_client_secret.json`

## Code Map

- `src/hora_finance/__main__.py`: CLI parsing and runtime dispatch.
- `src/hora_finance/app.py`: Flask routes and HTML shell.
- `src/hora_finance/google_auth.py`: desktop OAuth login and required scopes.
- `src/hora_finance/storage.py`: SQLite schema plus active session handling.
- `src/hora_finance/sheets.py`: Sheets API access and credential validation.
- `src/hora_finance/reporting.py`: row parsing, aggregation, and markdown output.

## Recent History

- `bf8b0be`: added Sheets client, report engine, CLI report command, `/reports/google-sheet`, and docs.
- 2026-03-15: verified GitHub user `aarshps`, closed issue `#1` (`Boardroom`) as completed.

## Operational Notes

- Use `./scripts/gh-aarshps ...` for GitHub CLI work in this repo.
- If a user signed in before Sheets support was added, they must log out and sign in again to grant the Sheets scope.
- Live report generation requires an active signed-in user stored in SQLite.
- Keep `.github/skills` current and within the 100-line limit when repo behavior changes.

## Suggested First Checks

```bash
git checkout main
git pull --ff-only origin main
git status --short
python -m pytest
python -m hora_finance check
```
