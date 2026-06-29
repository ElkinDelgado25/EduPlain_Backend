import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.domain.entities import UserRole

BOOTSTRAP_USERNAME_ENVIRONMENT_VARIABLE = "EDUPLAIN_BOOTSTRAP_ADMIN_USERNAME"
BOOTSTRAP_EMAIL_ENVIRONMENT_VARIABLE = "EDUPLAIN_BOOTSTRAP_ADMIN_EMAIL"
BOOTSTRAP_FULL_NAME_ENVIRONMENT_VARIABLE = "EDUPLAIN_BOOTSTRAP_ADMIN_FULL_NAME"
BOOTSTRAP_ROLE_ENVIRONMENT_VARIABLE = "EDUPLAIN_BOOTSTRAP_ADMIN_ROLE"
PASSWORD_ENVIRONMENT_VARIABLE = "EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD"


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise CommandError(f"{name} is required to create the superuser.")
    return value


class Command(BaseCommand):
    """Create the configured initial superuser exactly once."""

    help = "Create an initial superuser from environment variables when it does not exist."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--skip-if-unconfigured",
            action="store_true",
            help=f"Exit successfully when {PASSWORD_ENVIRONMENT_VARIABLE} is not configured.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        user_model = get_user_model()
        password = os.getenv(PASSWORD_ENVIRONMENT_VARIABLE, "").strip()

        if not password:
            if options["skip_if_unconfigured"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"Superuser bootstrap skipped: {PASSWORD_ENVIRONMENT_VARIABLE} "
                        "is not configured."
                    )
                )
                return
            raise CommandError(
                f"{PASSWORD_ENVIRONMENT_VARIABLE} is required to create the superuser."
            )

        username = required_env(BOOTSTRAP_USERNAME_ENVIRONMENT_VARIABLE)
        email = required_env(BOOTSTRAP_EMAIL_ENVIRONMENT_VARIABLE)
        full_name = required_env(BOOTSTRAP_FULL_NAME_ENVIRONMENT_VARIABLE)
        role = required_env(BOOTSTRAP_ROLE_ENVIRONMENT_VARIABLE)

        try:
            UserRole(role)
        except ValueError as exc:
            raise CommandError(
                f"{BOOTSTRAP_ROLE_ENVIRONMENT_VARIABLE} must be one of: "
                f"{', '.join(user_role.value for user_role in UserRole)}."
            ) from exc

        existing_user = user_model.objects.filter(username=username).first()
        if existing_user is not None:
            if existing_user.is_superuser:
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
                return
            raise CommandError(
                f"User '{username}' already exists but is not a superuser; refusing to elevate it."
            )

        if password == "CHANGE_ME":
            raise CommandError(
                f"{PASSWORD_ENVIRONMENT_VARIABLE} must not use the CHANGE_ME placeholder."
            )
        if user_model.objects.filter(email=email).exists():
            raise CommandError(
                f"Email '{email}' is already assigned to another user; superuser was not created."
            )

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            is_public=False,
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
