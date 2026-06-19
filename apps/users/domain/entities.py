from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    """Roles understood by the business, independent from Django."""

    STUDENT = "student"
    PROFESSOR = "professor"
    ADMINISTRATOR = "administrator"


@dataclass(frozen=True, slots=True)
class PublicUser:
    """Immutable domain representation safe for the public directory."""

    id: int
    full_name: str
    email: str
    role: UserRole
