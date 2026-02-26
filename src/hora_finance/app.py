from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template_string, url_for

from .config import AppConfig
from .google_auth import GoogleAuthError, login_with_google
from .storage import clear_active_session, get_active_user, set_active_session, upsert_user


INDEX_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Hora Finance</title>
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem auto; max-width: 760px; line-height: 1.4; }
      .card { border: 1px solid #ddd; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem; }
      a.button { display: inline-block; background: #0b57d0; color: #fff; text-decoration: none; padding: 0.6rem 1rem; border-radius: 8px; }
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
      <p><strong>Google client secret:</strong> <code>{{ client_secret_path }}</code></p>
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
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem auto; max-width: 760px; line-height: 1.4; }
      .card { border: 1px solid #c00; border-radius: 12px; padding: 1rem 1.25rem; background: #fff6f6; }
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

    return app
