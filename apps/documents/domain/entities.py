from dataclasses import dataclass


@dataclass(frozen=True)
class MarkdownDocument:
    filename: str
    markdown: str
    characters: int


@dataclass(frozen=True)
class StoredPdfDocument:
    id: str
    filename: str
    content_type: str
    size_bytes: int
    storage_backend: str
    storage_key: str
    created_at: str
