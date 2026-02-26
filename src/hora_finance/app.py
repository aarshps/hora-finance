from __future__ import annotations

from pathlib import Path

from flask import Flask, Response, jsonify, redirect, render_template_string, request, url_for

from .config import AppConfig
from .google_auth import GoogleAuthError, login_with_google
from .reporting import generate_report_from_google_sheet, save_report
from .sheets import SheetsError
from .storage import (
    clear_active_session,
    get_active_credentials_json,
    get_active_user,
    set_active_session,
    upsert_user,
)


INDEX_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Hora Finance</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 2rem auto;
        max-width: 760px;
        line-height: 1.4;
      }
      .card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
      }
      a.button {
        display: inline-block;
        background: #0b57d0;
        color: #fff;
        text-decoration: none;
        padding: 0.6rem 1rem;
        border-radius: 8px;
      }
      button {
        background: #0b57d0;
        color: #fff;
        border: 0;
        padding: 0.55rem 0.9rem;
        border-radius: 8px;
        cursor: pointer;
      }
      label { display: block; margin: 0.5rem 0 0.25rem; font-weight: 600; }
      input {
        width: 100%;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 0.55rem;
        margin-bottom: 0.5rem;
      }
      .muted { color: #666; }
      code { background: #f2f2f2; padding: 0.1rem 0.3rem; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1>Hora Finance</h1>
    <p class="muted">Local-only app. Auth and storage stay on your machine.</p>

    <div class="card">
      {% if user %}
        <p><strong>Signed in:</strong> {{ user.name or "Google user" }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><a class="button" href="{{ url_for('logout') }}">Logout</a></p>
      {% else %}
        <p>You are not signed in.</p>
        <p><a class="button" href="{{ url_for('google_login') }}">Sign in with Google</a></p>
      {% endif %}
    </div>

    <div class="card">
      <p><strong>Data dir:</strong> <code>{{ data_dir }}</code></p>
      <p><strong>SQLite DB:</strong> <code>{{ db_path }}</code></p>
      <p><strong>Reports dir:</strong> <code>{{ reports_dir }}</code></p>
      <p><strong>Google client secret:</strong> <code>{{ client_secret_path }}</code></p>
    </div>

    <div class="card">
      <h2>Google Sheets Finance Report</h2>
      {% if user %}
        <form action="{{ url_for('google_sheet_report') }}" method="get">
          <label for="spreadsheet_id">Spreadsheet ID</label>
          <input id="spreadsheet_id" name="spreadsheet_id" placeholder="1AbC..." required />

          <label for="range">Range (optional)</label>
          <input id="range" name="range" placeholder="Sheet1!A:Z" />

          <button type="submit">Generate Report</button>
        </form>
        <p class="muted">
          Endpoint: <code>/reports/google-sheet</code>.
          Add <code>&format=markdown</code> for markdown response.
        </p>
      {% else %}
        <p>Sign in with Google first to generate reports.</p>
      {% endif %}
    </div>
  </body>
</html>
"""


ERROR_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Auth Error</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 2rem auto;
        max-width: 760px;
        line-height: 1.4;
      }
      .card {
        border: 1px solid #c00;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        background: #fff6f6;
      }
      code { background: #f2f2f2; padding: 0.1rem 0.3rem; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1>Google Auth Error</h1>
    <div class="card">
      <p>{{ message }}</p>
      <p>Expected client secret path: <code>{{ client_secret_path }}</code></p>
      <p><a href="{{ url_for('index') }}">Back to home</a></p>
    </div>
  </body>
</html>
"""


def create_app(config: AppConfig) -> Flask:
    app = Flask(__name__)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "mode": "local-only"})

    @app.get("/me")
    def me():
        user = get_active_user(config.db_path)
        if user is None:
            return jsonify({"authenticated": False})
        return jsonify({"authenticated": True, "user": user})

    @app.get("/")
    def index():
        return render_template_string(
            INDEX_TEMPLATE,
            user=get_active_user(config.db_path),
            data_dir=str(config.data_dir),
            db_path=str(config.db_path),
            reports_dir=str(config.reports_dir),
            client_secret_path=str(config.google_client_secret_path),
        )

    @app.get("/auth/google/login")
    def google_login():
        try:
            user_info, credentials_json = login_with_google(config.google_client_secret_path)
        except GoogleAuthError as exc:
            return (
                render_template_string(
                    ERROR_TEMPLATE,
                    message=str(exc),
                    client_secret_path=str(config.google_client_secret_path),
                ),
                400,
            )

        user_id = upsert_user(config.db_path, user_info, credentials_json)
        set_active_session(config.db_path, user_id)
        return redirect(url_for("index"))

    @app.get("/logout")
    def logout():
        clear_active_session(config.db_path)
        return redirect(url_for("index"))

    @app.get("/reports/google-sheet")
    def google_sheet_report():
        spreadsheet_id = request.args.get("spreadsheet_id", "").strip()
        value_range = request.args.get("range", "").strip() or None
        output_path_arg = request.args.get("output_path", "").strip()
        output_path = Path(output_path_arg).expanduser() if output_path_arg else None
        output_format = request.args.get("format", "json").strip().lower()

        if not spreadsheet_id:
            return (
                jsonify({"error": "Missing required query parameter: spreadsheet_id"}),
                400,
            )

        credentials_json = get_active_credentials_json(config.db_path)
        if not credentials_json:
            return (
                jsonify({"error": "No active signed-in user. Sign in with Google first."}),
                401,
            )

        try:
            report_markdown, meta = generate_report_from_google_sheet(
                credentials_json=credentials_json,
                spreadsheet_id=spreadsheet_id,
                value_range=value_range,
            )
            saved_path = save_report(
                report_markdown=report_markdown,
                reports_dir=config.reports_dir,
                spreadsheet_id=spreadsheet_id,
                output_path=output_path,
            )
        except SheetsError as exc:
            return jsonify({"error": str(exc)}), 400

        if output_format == "markdown":
            return Response(
                report_markdown,
                mimetype="text/markdown",
                headers={"X-Hora-Report-Path": str(saved_path)},
            )

        return jsonify(
            {
                "spreadsheet_id": meta.spreadsheet_id,
                "range": meta.used_range,
                "transaction_count": meta.transaction_count,
                "output_path": str(saved_path),
            }
        )

    return app
