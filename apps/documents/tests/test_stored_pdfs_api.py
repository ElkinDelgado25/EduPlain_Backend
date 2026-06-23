import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def create_authenticated_client() -> APIClient:
    user = get_user_model().objects.create_user(
        username="docente",
        email="docente@example.edu",
        password="local-test-password",
        full_name="Docente Test",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_stored_pdfs_endpoint_requires_authentication() -> None:
    response = APIClient().get(reverse("documents:pdf-list"))

    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


@pytest.mark.django_db
def test_store_pdf_document_returns_metadata(tmp_path) -> None:
    client = create_authenticated_client()
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    with override_settings(DOCUMENT_STORAGE_ROOT=tmp_path):
        response = client.post(
            reverse("documents:pdf-list"),
            {"file": uploaded_file},
            format="multipart",
        )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["filename"] == "silabo.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size_bytes"] == 11
    assert data["storage_backend"] == "local"
    assert data["storage_key"].startswith("pdfs/")
    assert data["created_at"].endswith("Z")


@pytest.mark.django_db
def test_list_stored_pdf_documents_returns_metadata(tmp_path) -> None:
    client = create_authenticated_client()
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    with override_settings(DOCUMENT_STORAGE_ROOT=tmp_path):
        created = client.post(
            reverse("documents:pdf-list"),
            {"file": uploaded_file},
            format="multipart",
        ).json()
        response = client.get(reverse("documents:pdf-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [created]


@pytest.mark.django_db
def test_get_stored_pdf_document_returns_metadata(tmp_path) -> None:
    client = create_authenticated_client()
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    with override_settings(DOCUMENT_STORAGE_ROOT=tmp_path):
        created = client.post(
            reverse("documents:pdf-list"),
            {"file": uploaded_file},
            format="multipart",
        ).json()
        response = client.get(reverse("documents:pdf-detail", args=[created["id"]]))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created


@pytest.mark.django_db
def test_get_stored_pdf_document_returns_404_for_missing_document(tmp_path) -> None:
    client = create_authenticated_client()

    with override_settings(DOCUMENT_STORAGE_ROOT=tmp_path):
        response = client.get(reverse("documents:pdf-detail", args=["missing"]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
