import os
from pathlib import Path

from dotenv import dotenv_values


def load_local_env_files(base_dir: Path) -> None:
    """Load .env.local over .env without overriding real process variables."""

    process_keys = set(os.environ)
    for env_file in (base_dir / ".env", base_dir / ".env.local"):
        for key, value in dotenv_values(env_file).items():
            if value is not None and key not in process_keys:
                os.environ[key] = value
