"""Django model-discovery bridge.

The implementation remains in infrastructure; this import lets Django register
the model using its conventional ``<app>.models`` discovery mechanism.
"""

from apps.users.infrastructure.models import User

__all__ = ["User"]
