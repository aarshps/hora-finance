from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int
    data_dir: Path
    db_path: Path
    google_client_secret_path: Path


def load_config() -> AppConfig:
    data_dir = Path(
        os.environ.get("HORA_FINANCE_DATA_DIR", str(Path.home() / ".hora-finance"))
    ).expanduser()
    db_path = data_dir / "hora_finance.db"
    client_secret_default = data_dir / "google_client_secret.json"
    google_client_secret_path = Path(
        os.environ.get("HORA_FINANCE_GOOGLE_CLIENT_SECRET", str(client_secret_default))
    ).expanduser()

    return AppConfig(
        host=os.environ.get("HORA_FINANCE_HOST", "127.0.0.1"),
        port=int(os.environ.get("HORA_FINANCE_PORT", "8765")),
        data_dir=data_dir,
        db_path=db_path,
        google_client_secret_path=google_client_secret_path,
    )


def ensure_data_dir(config: AppConfig) -> None:
    config.data_dir.mkdir(parents=True, exist_ok=True)
