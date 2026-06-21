import pytest

from apps.documents.application.use_cases import (
    ConvertPdfToMarkdown,
    EmptyDocumentError,
    UnsupportedDocumentError,
)
from apps.documents.domain.entities import MarkdownDocument


class InMemoryMarkdownConverter:
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        return MarkdownDocument(filename=filename, markdown="# Extracted", characters=11)


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
