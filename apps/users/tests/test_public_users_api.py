import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.infrastructure.models import User


@pytest.mark.django_db
def test_public_users_endpoint_exposes_only_allowed_fields() -> None:
    User.objects.create_user(
        username="ada",
        email="ada@example.edu",
        password="local-test-password",
        full_name="Ada Lovelace",
        role="professor",
    )

    response = APIClient().get(reverse("users:public-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "full_name": "Ada Lovelace",
            "email": "ada@example.edu",
            "role": "professor",
        }
    ]


@pytest.mark.django_db
def test_public_users_endpoint_hides_private_and_inactive_users() -> None:
    User.objects.create_user(
        username="private",
        email="private@example.edu",
        password="local-test-password",
        full_name="Private User",
        is_public=False,
    )
    User.objects.create_user(
        username="inactive",
        email="inactive@example.edu",
        password="local-test-password",
        full_name="Inactive User",
        is_active=False,
    )

    response = APIClient().get(reverse("users:public-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
