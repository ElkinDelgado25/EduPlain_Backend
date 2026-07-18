import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.documents.domain.entities import MarkdownDocument
from apps.documents.interfaces.serializers import MAX_PDF_UPLOAD_SIZE_BYTES


class FakeMarkdownConverter:
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        return MarkdownDocument(
            filename=filename,
            markdown="# Unidad 1\n\nFunciones y limites",
            characters=30,
        )


@pytest.mark.django_db
def test_pdf_to_markdown_allows_unauthenticated_access(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.documents.interfaces.views.PyMuPDFMarkdownConverter",
        lambda: FakeMarkdownConverter(),
    )
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    response = APIClient().post(
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
    uploaded_file = SimpleUploadedFile("silabo.txt", b"text-content", content_type="text/plain")

    response = APIClient().post(
        reverse("documents:pdf-to-markdown"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"file": ["Only PDF files are supported."]}


@pytest.mark.django_db
def test_pdf_to_markdown_rejects_pdf_over_size_limit() -> None:
    uploaded_file = SimpleUploadedFile(
        "silabo.pdf",
        b"x" * (MAX_PDF_UPLOAD_SIZE_BYTES + 1),
        content_type="application/pdf",
    )

    response = APIClient().post(
        reverse("documents:pdf-to-markdown"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"file": ["PDF files must be 10 MB or smaller."]}
