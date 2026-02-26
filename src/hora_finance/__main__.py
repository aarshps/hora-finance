from __future__ import annotations

import argparse
from pathlib import Path

from .app import create_app
from .config import ensure_data_dir, load_config
from .reporting import generate_report_from_google_sheet, save_report
from .storage import get_active_credentials_json, init_db


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Hora Finance locally.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Legacy shortcut for `hora-finance check`.",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("serve", help="Start local web app (default).")
    subparsers.add_parser("check", help="Validate local config and initialize storage.")

    report_parser = subparsers.add_parser(
        "report",
        help="Fetch Google Sheet data and generate a finance report.",
    )
    report_parser.add_argument("--spreadsheet-id", required=True, help="Google spreadsheet ID.")
    report_parser.add_argument(
        "--range",
        dest="value_range",
        default="",
        help="Optional range (example: Sheet1!A:Z).",
    )
    report_parser.add_argument(
        "--output",
        default="",
        help="Optional output path for markdown report.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    config = load_config()
    ensure_data_dir(config)
    init_db(config.db_path)

    command = args.command
    if args.check and command is None:
        command = "check"
    if command is None:
        command = "serve"

    if command == "check":
        print("Config OK")
        print(f"Data dir: {config.data_dir}")
        print(f"DB path: {config.db_path}")
        print(f"Reports dir: {config.reports_dir}")
        print(f"Google client secret path: {config.google_client_secret_path}")
        return

    if command == "report":
        credentials_json = get_active_credentials_json(config.db_path)
        if not credentials_json:
            raise SystemExit("No active signed-in user. Sign in with Google first.")

        report_markdown, meta = generate_report_from_google_sheet(
            credentials_json=credentials_json,
            spreadsheet_id=args.spreadsheet_id,
            value_range=args.value_range or None,
        )
        output_path = Path(args.output).expanduser() if args.output else None
        saved = save_report(
            report_markdown=report_markdown,
            reports_dir=config.reports_dir,
            spreadsheet_id=args.spreadsheet_id,
            output_path=output_path,
        )
        print(f"Report generated from range: {meta.used_range}")
        print(f"Transactions processed: {meta.transaction_count}")
        print(f"Output: {saved}")
        return

    app = create_app(config)
    print(f"Starting Hora Finance on http://{config.host}:{config.port}")
    print(f"Local data dir: {config.data_dir}")
    print(f"Local reports dir: {config.reports_dir}")
    app.run(host=config.host, port=config.port, debug=False)


if __name__ == "__main__":
    main()
