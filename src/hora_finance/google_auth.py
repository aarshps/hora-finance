from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import InstalledAppFlow


GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


class GoogleAuthError(RuntimeError):
    pass


def login_with_google(client_secret_path: Path) -> tuple[dict[str, str], str]:
    if not client_secret_path.exists():
        raise GoogleAuthError(
            f"Google client secret file not found at: {client_secret_path}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        scopes=GOOGLE_SCOPES,
    )
    credentials = flow.run_local_server(
        host="127.0.0.1",
        port=0,
        open_browser=True,
        authorization_prompt_message="Opening browser for Google login...",
        success_message="Google login complete. Return to Hora Finance.",
    )

    session = AuthorizedSession(credentials)
    response = session.get("https://openidconnect.googleapis.com/v1/userinfo", timeout=15)
    if response.status_code != 200:
        raise GoogleAuthError(f"Failed to fetch Google user profile ({response.status_code}).")

    data = response.json()
    if "sub" not in data or "email" not in data:
        raise GoogleAuthError("Google response is missing required user fields.")

    user_info = {
        "sub": data.get("sub", ""),
        "email": data.get("email", ""),
        "name": data.get("name", ""),
        "picture": data.get("picture", ""),
    }
    return user_info, credentials.to_json()
