import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.domain.entities import UserRole

BOOTSTRAP_USERNAME = "eduplain_su_owner"
BOOTSTRAP_EMAIL = "owner@eduplain.local"
BOOTSTRAP_FULL_NAME = "Eduplain System Owner"
PASSWORD_ENVIRONMENT_VARIABLE = "EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD"


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
        username = BOOTSTRAP_USERNAME

        existing_user = user_model.objects.filter(username=username).first()
        if existing_user is not None:
            if existing_user.is_superuser:
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
                return
            raise CommandError(
                f"User '{username}' already exists but is not a superuser; refusing to elevate it."
            )

        password = os.getenv(PASSWORD_ENVIRONMENT_VARIABLE, "")

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

        if password == "CHANGE_ME":
            raise CommandError(
                f"{PASSWORD_ENVIRONMENT_VARIABLE} must not use the CHANGE_ME placeholder."
            )
        if user_model.objects.filter(email=BOOTSTRAP_EMAIL).exists():
            raise CommandError(
                f"Email '{BOOTSTRAP_EMAIL}' is already assigned to another user; "
                "superuser was not created."
            )

        user_model.objects.create_superuser(
            username=username,
            email=BOOTSTRAP_EMAIL,
            password=password,
            full_name=BOOTSTRAP_FULL_NAME,
            role=UserRole.ADMINISTRATOR.value,
            is_public=False,
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
