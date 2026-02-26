# hora-finance

Lightweight, local-first personal finance app.

Design goals:
- Runs only on local machines (no server deployment required)
- Google sign-in for local user auth
- Local SQLite storage only
- Minimal dependencies

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

## Local storage

- Data directory default: `~/.hora-finance`
- SQLite database: `~/.hora-finance/hora_finance.db`

## Config check (no server start)

```bash
source .venv/bin/activate
python -m hora_finance --check
```
