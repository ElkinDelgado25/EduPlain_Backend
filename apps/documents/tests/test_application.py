import pytest

from apps.documents.application.use_cases import (
    ConvertPdfToMarkdown,
    EmptyDocumentError,
    GetStoredPdfDocument,
    ListStoredPdfDocuments,
    SavePdfDocument,
    UnsupportedDocumentError,
)
from apps.documents.domain.entities import MarkdownDocument, StoredPdfDocument


class InMemoryMarkdownConverter:
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        return MarkdownDocument(filename=filename, markdown="# Extracted", characters=11)


class InMemoryPdfDocumentStorage:
    def __init__(self) -> None:
        self.documents = [
            StoredPdfDocument(
                id="doc-1",
                filename="silabo.pdf",
                content_type="application/pdf",
                size_bytes=11,
                storage_backend="memory",
                storage_key="pdfs/doc-1.pdf",
                created_at="2026-01-01T00:00:00Z",
            )
        ]

    def save_pdf(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> StoredPdfDocument:
        document = StoredPdfDocument(
            id="doc-2",
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            storage_backend="memory",
            storage_key="pdfs/doc-2.pdf",
            created_at="2026-01-02T00:00:00Z",
        )
        self.documents.append(document)
        return document

    def list_pdfs(self) -> list[StoredPdfDocument]:
        return self.documents

    def get_pdf(self, document_id: str) -> StoredPdfDocument:
        return next(document for document in self.documents if document.id == document_id)


def test_convert_pdf_to_markdown_returns_converter_result() -> None:
    result = ConvertPdfToMarkdown(InMemoryMarkdownConverter()).execute(
        filename="silabo.pdf",
        content=b"pdf-content",
    )

    assert result == MarkdownDocument(filename="silabo.pdf", markdown="# Extracted", characters=11)


def test_convert_pdf_to_markdown_rejects_non_pdf_documents() -> None:
    with pytest.raises(UnsupportedDocumentError):
        ConvertPdfToMarkdown(InMemoryMarkdownConverter()).execute(
            filename="silabo.txt",
            content=b"plain-text",
        )


def test_convert_pdf_to_markdown_rejects_empty_documents() -> None:
    with pytest.raises(EmptyDocumentError):
        ConvertPdfToMarkdown(InMemoryMarkdownConverter()).execute(
            filename="silabo.pdf",
            content=b"",
        )


def test_save_pdf_document_returns_storage_result() -> None:
    result = SavePdfDocument(InMemoryPdfDocumentStorage()).execute(
        filename="silabo.pdf",
        content=b"pdf-content",
        content_type="application/pdf",
    )

    assert result.id == "doc-2"
    assert result.filename == "silabo.pdf"
    assert result.size_bytes == 11


def test_save_pdf_document_rejects_non_pdf_documents() -> None:
    with pytest.raises(UnsupportedDocumentError):
        SavePdfDocument(InMemoryPdfDocumentStorage()).execute(
            filename="silabo.txt",
            content=b"plain-text",
            content_type="text/plain",
        )


def test_list_stored_pdf_documents_returns_storage_results() -> None:
    result = ListStoredPdfDocuments(InMemoryPdfDocumentStorage()).execute()

    assert [document.id for document in result] == ["doc-1"]


def test_get_stored_pdf_document_returns_storage_result() -> None:
    result = GetStoredPdfDocument(InMemoryPdfDocumentStorage()).execute(document_id="doc-1")

    assert result.filename == "silabo.pdf"
