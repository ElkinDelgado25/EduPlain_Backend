import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.domain.entities import UserRole


class Command(BaseCommand):
    """Create the configured initial superuser exactly once."""

    help = "Create an initial superuser from environment variables when it does not exist."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--skip-if-unconfigured",
            action="store_true",
            help="Exit successfully when DJANGO_SUPERUSER_PASSWORD is not configured.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        user_model = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "elkin").strip()

        existing_user = user_model.objects.filter(username=username).first()
        if existing_user is not None:
            if existing_user.is_superuser:
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
                return
            raise CommandError(
                f"User '{username}' already exists but is not a superuser; refusing to elevate it."
            )

        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "elkindelgado05@gmail.com").strip()
        full_name = os.getenv("DJANGO_SUPERUSER_FULL_NAME", "Elkin Delgado").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not password:
            if options["skip_if_unconfigured"]:
                self.stdout.write(
                    self.style.WARNING(
                        "Superuser bootstrap skipped: DJANGO_SUPERUSER_PASSWORD is not configured."
                    )
                )
                return
            raise CommandError("DJANGO_SUPERUSER_PASSWORD is required to create the superuser.")

        if password == "CHANGE_ME":
            raise CommandError("DJANGO_SUPERUSER_PASSWORD must not use the CHANGE_ME placeholder.")
        if not email:
            raise CommandError("DJANGO_SUPERUSER_EMAIL must not be empty.")
        if not full_name:
            raise CommandError("DJANGO_SUPERUSER_FULL_NAME must not be empty.")
        if user_model.objects.filter(email=email).exists():
            raise CommandError(
                f"Email '{email}' is already assigned to another user; superuser was not created."
            )

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole.ADMINISTRATOR.value,
            is_public=False,
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
