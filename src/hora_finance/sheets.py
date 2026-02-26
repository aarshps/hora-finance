from __future__ import annotations

import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SHEETS_READ_SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"


class SheetsError(RuntimeError):
    pass


def _credentials_from_json(credentials_json: str) -> Credentials:
    try:
        payload = json.loads(credentials_json)
    except json.JSONDecodeError as exc:
        raise SheetsError("Stored credentials are invalid JSON.") from exc

    creds = Credentials.from_authorized_user_info(payload)
    if not creds.has_scopes([SHEETS_READ_SCOPE]):
        raise SheetsError(
            "Google credentials are missing Sheets permission. "
            "Log out and sign in again to grant Sheets access."
        )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds.valid:
        raise SheetsError("Google credentials are invalid. Please sign in again.")

    return creds


def _resolve_default_range(service, spreadsheet_id: str) -> str:
    try:
        data = (
            service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id, fields="sheets(properties(title))")
            .execute()
        )
    except HttpError as exc:
        raise SheetsError(f"Failed to read spreadsheet metadata: {exc}") from exc

    sheets = data.get("sheets", [])
    if not sheets:
        raise SheetsError("Spreadsheet has no sheets.")
    title = sheets[0].get("properties", {}).get("title", "Sheet1")
    return f"{title}!A:Z"


def fetch_sheet_rows(
    credentials_json: str,
    spreadsheet_id: str,
    value_range: str | None = None,
) -> tuple[str, list[list[str]]]:
    creds = _credentials_from_json(credentials_json)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    resolved_range = value_range or _resolve_default_range(service, spreadsheet_id)

    try:
        values_data = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=resolved_range, majorDimension="ROWS")
            .execute()
        )
    except HttpError as exc:
        raise SheetsError(f"Failed to fetch rows from spreadsheet: {exc}") from exc

    rows = values_data.get("values", [])
    if not rows:
        raise SheetsError("No rows found in the selected range.")

    normalized_rows: list[list[str]] = []
    for row in rows:
        normalized_rows.append([str(cell) for cell in row])
    return resolved_range, normalized_rows
