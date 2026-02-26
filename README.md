# hora-finance

Lightweight, local-first personal finance app.

Design goals:
- Runs only on local machines (no server deployment required)
- Google sign-in for local user auth
- Local SQLite storage only
- Minimal dependencies
- Google Sheets ingestion for report generation

## Python version

This repo targets Python `3.14.x` and is pinned to `3.14.2` in `.python-version`.

## Setup

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Google auth setup (local)

1. In Google Cloud Console, create OAuth credentials for a Desktop app.
2. Download the client secret JSON.
3. Save it at:
   - `~/.hora-finance/google_client_secret.json` (default), or
   - set `HORA_FINANCE_GOOGLE_CLIENT_SECRET` to a custom path.

## Run locally

```bash
source .venv/bin/activate
python -m hora_finance
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765) and click `Sign in with Google`.

If you had already signed in before Sheets support was added, sign out and sign in again so
`spreadsheets.readonly` permission is granted.

## Local storage

- Data directory default: `~/.hora-finance`
- SQLite database: `~/.hora-finance/hora_finance.db`
- Reports directory: `~/.hora-finance/reports`

## Config check (no server start)

```bash
source .venv/bin/activate
python -m hora_finance --check
```

## Generate finance report from Google Sheets

CLI:

```bash
source .venv/bin/activate
python -m hora_finance report --spreadsheet-id "<SPREADSHEET_ID>" --range "Sheet1!A:Z"
```

Optional output path:

```bash
python -m hora_finance report --spreadsheet-id "<SPREADSHEET_ID>" --output ~/Downloads/report.md
```

HTTP endpoint (when app is running and signed in):

```text
GET /reports/google-sheet?spreadsheet_id=<SPREADSHEET_ID>&range=Sheet1!A:Z
```

For direct markdown response:

```text
GET /reports/google-sheet?spreadsheet_id=<SPREADSHEET_ID>&format=markdown
```
