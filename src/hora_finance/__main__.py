from __future__ import annotations

import argparse

from .app import create_app
from .config import ensure_data_dir, load_config
from .storage import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Hora Finance locally.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate local config and initialize storage, then exit.",
    )
    args = parser.parse_args()

    config = load_config()
    ensure_data_dir(config)
    init_db(config.db_path)

    if args.check:
        print("Config OK")
        print(f"Data dir: {config.data_dir}")
        print(f"DB path: {config.db_path}")
        print(f"Google client secret path: {config.google_client_secret_path}")
        return

    app = create_app(config)
    print(f"Starting Hora Finance on http://{config.host}:{config.port}")
    print(f"Local data dir: {config.data_dir}")
    app.run(host=config.host, port=config.port, debug=False)


if __name__ == "__main__":
    main()
