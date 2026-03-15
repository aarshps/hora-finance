---
name: google-sheets-reporting
description: Workflow and failure modes for Google auth, Sheets ingestion, and finance report generation.
---

# Google Sheets Reporting

Use this skill when touching sign-in, Sheets fetch, or report output.

## Invariants

- The app is local-only; do not add remote persistence or hosted-server assumptions.
- Sheets access depends on `https://www.googleapis.com/auth/spreadsheets.readonly`.
- The CLI `report` flow and `/reports/google-sheet` endpoint both require an active signed-in user in SQLite.
- Reports save under `HORA_FINANCE_REPORTS_DIR` or `~/.hora-finance/reports`.

## Common Failures

- Missing client secret: place JSON at `~/.hora-finance/google_client_secret.json` or set `HORA_FINANCE_GOOGLE_CLIENT_SECRET`.
- Old credentials missing Sheets scope: log out and sign in again.
- No active session: sign in from the web app before running `python -m hora_finance report ...`.
- Empty or invalid sheet data: `reporting.py` requires a header row and an amount-like column.

## Useful Checks

- `python -m hora_finance check`
- `python -m hora_finance report --spreadsheet-id "<id>" --range "Sheet1!A:Z"`
- `GET /reports/google-sheet?spreadsheet_id=<id>&format=markdown`
