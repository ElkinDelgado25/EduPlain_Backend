from pathlib import Path

from .env_loader import load_local_env_files

BASE_DIR = Path(__file__).resolve().parents[2]

load_local_env_files(BASE_DIR)

from .base import *  # noqa: E402,F403

# Development keeps the browsable API available for easier local inspection.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [  # noqa: F405
    "rest_framework.renderers.BrowsableAPIRenderer"
]

CORS_ALLOWED_ORIGINS = env_list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
CORS_ALLOW_HEADERS = [  # noqa: F405
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
]
