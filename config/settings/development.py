from pathlib import Path

from dotenv import load_dotenv

# Local development reads the repository .env before base settings require values.
# Existing process variables keep precedence, matching Docker and CI behavior.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from .base import *  # noqa: E402,F403

# Development keeps the browsable API available for easier local inspection.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [  # noqa: F405
    "rest_framework.renderers.BrowsableAPIRenderer"
]
