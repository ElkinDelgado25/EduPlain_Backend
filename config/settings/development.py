from pathlib import Path

from .env_loader import load_local_env_files

BASE_DIR = Path(__file__).resolve().parents[2]

load_local_env_files(BASE_DIR)

from .base import *  # noqa: E402,F403

# Development keeps the browsable API available for easier local inspection.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [  # noqa: F405
    "rest_framework.renderers.BrowsableAPIRenderer"
]
