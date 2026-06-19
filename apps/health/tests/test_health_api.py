from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@override_settings(ENVIRONMENT="test")
def test_health_endpoint_is_public() -> None:
    response = APIClient().get(reverse("health:check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
        "service": "eduplain-backend",
        "environment": "test",
    }
