import json
from dataclasses import asdict
from datetime import UTC, datetime
from json import JSONDecodeError
from pathlib import Path
from uuid import uuid4

from django.conf import settings

from apps.documents.application.use_cases import DocumentStorageError, StoredPdfNotFoundError
from apps.documents.domain.entities import StoredPdfDocument


class LocalPdfDocumentStorage:
    """Store PDFs and a small metadata catalog on the local filesystem."""

    backend_name = "local"

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.pdfs_root = self.root / "pdfs"
        self.catalog_path = self.root / "catalog.json"

    def save_pdf(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> StoredPdfDocument:
        document_id = uuid4().hex
        storage_key = f"pdfs/{document_id}.pdf"
        pdf_path = self.pdfs_root / f"{document_id}.pdf"
        created_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        try:
            self.pdfs_root.mkdir(parents=True, exist_ok=True)
            pdf_path.write_bytes(content)
            document = StoredPdfDocument(
                id=document_id,
                filename=filename,
                content_type=content_type or "application/pdf",
                size_bytes=len(content),
                storage_backend=self.backend_name,
                storage_key=storage_key,
                created_at=created_at,
            )
            catalog = self._read_catalog()
            catalog.append(asdict(document))
            self._write_catalog(catalog)
        except OSError as exc:
            raise DocumentStorageError("The PDF could not be stored locally.") from exc

        return document

    def list_pdfs(self) -> list[StoredPdfDocument]:
        return [StoredPdfDocument(**item) for item in reversed(self._read_catalog())]

    def get_pdf(self, document_id: str) -> StoredPdfDocument:
        for item in self._read_catalog():
            if item["id"] == document_id:
                return StoredPdfDocument(**item)
        raise StoredPdfNotFoundError("Stored PDF document was not found.")

    def _read_catalog(self) -> list[dict[str, str | int]]:
        if not self.catalog_path.exists():
            return []
        try:
            data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except (JSONDecodeError, OSError) as exc:
            raise DocumentStorageError("The local PDF catalog could not be read.") from exc
        if not isinstance(data, list):
            raise DocumentStorageError("The local PDF catalog has an invalid format.")
        return data

    def _write_catalog(self, catalog: list[dict[str, str | int]]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def get_pdf_document_storage() -> LocalPdfDocumentStorage:
    if settings.DOCUMENT_STORAGE_BACKEND != "local":
        raise DocumentStorageError(
            f"Document storage backend '{settings.DOCUMENT_STORAGE_BACKEND}' is not implemented."
        )
    return LocalPdfDocumentStorage(root=settings.DOCUMENT_STORAGE_ROOT)
