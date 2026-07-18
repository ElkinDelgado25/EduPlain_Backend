import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.ai_agents.application.use_cases import PHASE_1_VERSION
from apps.ai_agents.infrastructure.generic_syllabus_analyzer import (
    GENERIC_NOTES,
    GENERIC_OBJECTIVE,
)
from apps.ai_agents.interfaces.serializers import MAX_PDF_UPLOAD_SIZE_BYTES
from apps.documents.domain.entities import MarkdownDocument


class FakeMarkdownConverter:
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        markdown = "# Unidad 1\n\nFunciones y limites"
        return MarkdownDocument(filename=filename, markdown=markdown, characters=len(markdown))


@pytest.mark.django_db
def test_syllabus_analyze_requires_authentication() -> None:
    uploaded_file = SimpleUploadedFile("silabo.pdf", b"pdf-content", content_type="application/pdf")

    response = APIClient().post(
        reverse("ai_agents:syllabus-analyze"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


@pytest.mark.django_db
def test_syllabus_analyze_returns_generic_response_for_authenticated_user(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.ai_agents.interfaces.views.PyMuPDFMarkdownConverter",
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
        reverse("ai_agents:syllabus-analyze"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["filename"] == "silabo.pdf"
    markdown = "# Unidad 1\n\nFunciones y limites"
    assert payload["characters_extracted"] == len(markdown)
    assert payload["markdown_preview"] == "# Unidad 1\n\nFunciones y limites"
    assert payload["analysis"]["course_name"] is None
    assert payload["analysis"]["general_objective"] == GENERIC_OBJECTIVE
    assert payload["analysis"]["units"] == []
    assert payload["analysis"]["confidence"] == "generic"
    assert payload["analysis"]["notes"] == GENERIC_NOTES
    assert payload["phase"] == 1
    assert payload["agent"] == "syllabus-analyzer"
    assert payload["version"] == PHASE_1_VERSION
    assert payload["steps_completed"] == [
        "pdf_received",
        "markdown_extracted",
        "analysis_generated",
    ]


@pytest.mark.django_db
def test_syllabus_analyze_rejects_non_pdf_files() -> None:
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
        reverse("ai_agents:syllabus-analyze"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"file": ["Only PDF files are supported."]}


@pytest.mark.django_db
def test_syllabus_analyze_rejects_pdf_over_size_limit() -> None:
    user = get_user_model().objects.create_user(
        username="docente",
        email="docente@example.edu",
        password="local-test-password",
        full_name="Docente Test",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    uploaded_file = SimpleUploadedFile(
        "silabo.pdf",
        b"x" * (MAX_PDF_UPLOAD_SIZE_BYTES + 1),
        content_type="application/pdf",
    )

    response = client.post(
        reverse("ai_agents:syllabus-analyze"),
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"file": ["PDF files must be 10 MB or smaller."]}
