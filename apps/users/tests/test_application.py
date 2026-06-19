from collections.abc import Sequence

from apps.users.application.use_cases import ListPublicUsers
from apps.users.domain.entities import PublicUser, UserRole


class InMemoryPublicUserRepository:
    def __init__(self, users: Sequence[PublicUser]) -> None:
        self._users = users

    def list_public(self) -> Sequence[PublicUser]:
        return self._users


def test_list_public_users_returns_repository_entities() -> None:
    expected = [
        PublicUser(
            id=1,
            full_name="Ada Lovelace",
            email="ada@example.edu",
            role=UserRole.PROFESSOR,
        )
    ]

    result = ListPublicUsers(InMemoryPublicUserRepository(expected)).execute()

    assert result == expected
