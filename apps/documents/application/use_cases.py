from typing import Protocol

from apps.documents.domain.entities import MarkdownDocument, StoredPdfDocument


class DocumentConversionError(Exception):
    """Raised when a document cannot be converted to Markdown."""


class EmptyDocumentError(DocumentConversionError):
    """Raised when the uploaded document has no content."""


class UnsupportedDocumentError(DocumentConversionError):
    """Raised when the document type is not supported by the use case."""


class DocumentStorageError(Exception):
    """Raised when a document cannot be stored or queried."""


class StoredPdfNotFoundError(DocumentStorageError):
    """Raised when a stored PDF cannot be found."""


class MarkdownConverter(Protocol):
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument: ...


class PdfDocumentStorage(Protocol):
    def save_pdf(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> StoredPdfDocument: ...

    def list_pdfs(self) -> list[StoredPdfDocument]: ...

    def get_pdf(self, document_id: str) -> StoredPdfDocument: ...


class ConvertPdfToMarkdown:
    def __init__(self, converter: MarkdownConverter) -> None:
        self.converter = converter

    def execute(self, *, filename: str, content: bytes) -> MarkdownDocument:
        if not filename.lower().endswith(".pdf"):
            raise UnsupportedDocumentError("Only PDF documents can be converted to Markdown.")
        if not content:
            raise EmptyDocumentError("The uploaded PDF is empty.")

        return self.converter.convert(filename=filename, content=content)


class SavePdfDocument:
    def __init__(self, storage: PdfDocumentStorage) -> None:
        self.storage = storage

    def execute(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str = "application/pdf",
    ) -> StoredPdfDocument:
        if not filename.lower().endswith(".pdf"):
            raise UnsupportedDocumentError("Only PDF documents can be stored.")
        if not content:
            raise EmptyDocumentError("The uploaded PDF is empty.")

        return self.storage.save_pdf(
            filename=filename,
            content=content,
            content_type=content_type,
        )


class ListStoredPdfDocuments:
    def __init__(self, storage: PdfDocumentStorage) -> None:
        self.storage = storage

    def execute(self) -> list[StoredPdfDocument]:
        return self.storage.list_pdfs()


class GetStoredPdfDocument:
    def __init__(self, storage: PdfDocumentStorage) -> None:
        self.storage = storage

    def execute(self, *, document_id: str) -> StoredPdfDocument:
        return self.storage.get_pdf(document_id)
