import sys
from types import SimpleNamespace

import pytest

from apps.documents.application.use_cases import DocumentConversionError
from apps.documents.infrastructure.pdf_to_markdown import PyMuPDFMarkdownConverter


def test_pymupdf_converter_returns_stripped_markdown(monkeypatch) -> None:
    monkeypatch.setitem(
        sys.modules,
        "pymupdf4llm",
        SimpleNamespace(to_markdown=lambda path: "  # Unidad 1\n\nContenido  "),
    )

    result = PyMuPDFMarkdownConverter().convert(filename="silabo.pdf", content=b"pdf-content")

    assert result.filename == "silabo.pdf"
    assert result.markdown == "# Unidad 1\n\nContenido"
    assert result.characters == 21


def test_pymupdf_converter_rejects_empty_markdown(monkeypatch) -> None:
    monkeypatch.setitem(
        sys.modules,
        "pymupdf4llm",
        SimpleNamespace(to_markdown=lambda path: "   "),
    )

    with pytest.raises(DocumentConversionError, match="No readable text"):
        PyMuPDFMarkdownConverter().convert(filename="silabo.pdf", content=b"pdf-content")
