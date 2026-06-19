from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.domain.entities import UserRole


class User(AbstractUser):
    """Django persistence model; it must not leak into the domain layer."""

    full_name = models.CharField(max_length=160)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.name.title()) for role in UserRole],
        default=UserRole.STUDENT.value,
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Controls whether the user appears in the public directory.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("full_name", "id")
        verbose_name = "academic user"
        verbose_name_plural = "academic users"

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"
