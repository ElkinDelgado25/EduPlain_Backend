from collections.abc import Sequence

from apps.users.domain.entities import PublicUser, UserRole
from apps.users.infrastructure.models import User


class DjangoPublicUserRepository:
    """Django ORM adapter for the repository port defined by the application."""

    def list_public(self) -> Sequence[PublicUser]:
        rows = User.objects.filter(is_active=True, is_public=True).values(
            "id", "full_name", "email", "role"
        )
        return [
            PublicUser(
                id=row["id"],
                full_name=row["full_name"],
                email=row["email"],
                role=UserRole(row["role"]),
            )
            for row in rows
        ]
