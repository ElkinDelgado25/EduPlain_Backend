import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.documents.domain.entities import MarkdownDocument


class FakeMarkdownConverter:
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        return MarkdownDocument(
            filename=filename,
            markdown="# Unidad 1\n\nFunciones y limites",
            characters=30,
        )


@pytest.mark.django_db
def test_pdf_to_markdown_requires_authentication() -> None:
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    response = APIClient().post(
        reverse("documents:pdf-to-markdown"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


@pytest.mark.django_db
def test_pdf_to_markdown_returns_markdown_for_authenticated_user(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.documents.interfaces.views.PyMuPDFMarkdownConverter",
        lambda: FakeMarkdownConverter(),
    )
    user = get_user_model().objects.create_user(
        username="docente",
        email="docente@example.edu",
        password="local-test-password",
        full_name="Docente Test",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    response = client.post(
        reverse("documents:pdf-to-markdown"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "filename": "silabo.pdf",
        "characters": 30,
        "markdown": "# Unidad 1\n\nFunciones y limites",
    }


@pytest.mark.django_db
def test_pdf_to_markdown_rejects_non_pdf_files() -> None:
    user = get_user_model().objects.create_user(
        username="docente",
        email="docente@example.edu",
        password="local-test-password",
        full_name="Docente Test",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    uploaded_file = SimpleUploadedFile("silabo.txt", b"text-content", content_type="text/plain")

    response = client.post(
        reverse("documents:pdf-to-markdown"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"file": ["Only PDF files are supported."]}
