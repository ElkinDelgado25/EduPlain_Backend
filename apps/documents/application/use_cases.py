from typing import Protocol

from apps.documents.domain.entities import MarkdownDocument


class DocumentConversionError(Exception):
    """Raised when a document cannot be converted to Markdown."""


class EmptyDocumentError(DocumentConversionError):
    """Raised when the uploaded document has no content."""


class UnsupportedDocumentError(DocumentConversionError):
    """Raised when the document type is not supported by the use case."""


class MarkdownConverter(Protocol):
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument: ...


class ConvertPdfToMarkdown:
    def __init__(self, converter: MarkdownConverter) -> None:
        self.converter = converter

    def execute(self, *, filename: str, content: bytes) -> MarkdownDocument:
        if not filename.lower().endswith(".pdf"):
            raise UnsupportedDocumentError("Only PDF documents can be converted to Markdown.")
        if not content:
            raise EmptyDocumentError("The uploaded PDF is empty.")

        return self.converter.convert(filename=filename, content=content)
