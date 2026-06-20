import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.users.domain.entities import UserRole


@pytest.mark.django_db
def test_standard_manager_creates_private_administrator() -> None:
    user = get_user_model().objects.create_superuser(
        username="admin",
        email="admin@example.edu",
        password="strong-local-test-password",
        full_name="Admin User",
    )

    assert get_user_model().REQUIRED_FIELDS == ["email", "full_name"]
    assert user.role == UserRole.ADMINISTRATOR.value
    assert user.is_public is False


@pytest.mark.django_db
def test_bootstrap_superuser_creates_configured_administrator(monkeypatch) -> None:
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "elkin")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "elkindelgado05@gmail.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_FULL_NAME", "Elkin Delgado")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "strong-local-test-password")

    call_command("bootstrap_superuser")

    user = get_user_model().objects.get(username="elkin")
    assert user.email == "elkindelgado05@gmail.com"
    assert user.full_name == "Elkin Delgado"
    assert user.role == UserRole.ADMINISTRATOR.value
    assert user.is_superuser is True
    assert user.is_staff is True
    assert user.is_public is False
    assert user.check_password("strong-local-test-password")


@pytest.mark.django_db
def test_bootstrap_superuser_is_idempotent(monkeypatch) -> None:
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "strong-local-test-password")

    call_command("bootstrap_superuser")
    call_command("bootstrap_superuser")

    assert get_user_model().objects.filter(username="elkin", is_superuser=True).count() == 1


@pytest.mark.django_db
def test_bootstrap_superuser_can_skip_when_password_is_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)

    call_command("bootstrap_superuser", skip_if_unconfigured=True)

    assert not get_user_model().objects.filter(is_superuser=True).exists()


@pytest.mark.django_db
def test_bootstrap_superuser_refuses_to_elevate_existing_user(monkeypatch) -> None:
    get_user_model().objects.create_user(
        username="elkin",
        email="elkindelgado05@gmail.com",
        password="regular-user-password",
        full_name="Elkin Delgado",
    )
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "strong-local-test-password")

    with pytest.raises(CommandError, match="refusing to elevate"):
        call_command("bootstrap_superuser")
