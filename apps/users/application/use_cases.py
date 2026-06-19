from collections.abc import Sequence
from typing import Protocol

from apps.users.domain.entities import PublicUser


class PublicUserRepository(Protocol):
    """Port required by the application layer to obtain public users."""

    def list_public(self) -> Sequence[PublicUser]: ...


class ListPublicUsers:
    """Use case that coordinates the public academic directory query."""

    def __init__(self, repository: PublicUserRepository) -> None:
        self._repository = repository

    def execute(self) -> Sequence[PublicUser]:
        return self._repository.list_public()
