import pytest

from apps.documents.application.use_cases import StoredPdfNotFoundError
from apps.documents.infrastructure.storage import LocalPdfDocumentStorage


def test_local_pdf_document_storage_saves_and_lists_metadata(tmp_path) -> None:
    storage = LocalPdfDocumentStorage(root=tmp_path)

    document = storage.save_pdf(
        filename="Sílabo Cálculo.pdf",
        content=b"pdf-content",
        content_type="application/pdf",
    )

    assert document.filename == "Sílabo Cálculo.pdf"
    assert document.size_bytes == 11
    assert document.storage_backend == "local"
    assert (tmp_path / document.storage_key).read_bytes() == b"pdf-content"
    assert storage.list_pdfs() == [document]
    assert storage.get_pdf(document.id) == document


def test_local_pdf_document_storage_returns_newest_first(tmp_path) -> None:
    storage = LocalPdfDocumentStorage(root=tmp_path)

    first = storage.save_pdf(
        filename="first.pdf",
        content=b"first",
        content_type="application/pdf",
    )
    second = storage.save_pdf(
        filename="second.pdf",
        content=b"second",
        content_type="application/pdf",
    )

    assert storage.list_pdfs() == [second, first]


def test_local_pdf_document_storage_raises_when_document_is_missing(tmp_path) -> None:
    storage = LocalPdfDocumentStorage(root=tmp_path)

    with pytest.raises(StoredPdfNotFoundError):
        storage.get_pdf("missing")
