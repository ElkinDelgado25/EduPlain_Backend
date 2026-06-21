from pathlib import Path
from tempfile import TemporaryDirectory

from apps.documents.application.use_cases import DocumentConversionError
from apps.documents.domain.entities import MarkdownDocument


class PyMuPDFMarkdownConverter:
    """Convert PDF bytes to Markdown using a local temporary file."""

    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        try:
            import pymupdf4llm

            with TemporaryDirectory() as temporary_directory:
                pdf_path = Path(temporary_directory) / "input.pdf"
                pdf_path.write_bytes(content)
                markdown = pymupdf4llm.to_markdown(str(pdf_path)).strip()
        except Exception as exc:
            raise DocumentConversionError("The uploaded PDF could not be converted.") from exc

        if not markdown:
            raise DocumentConversionError("No readable text was extracted from the uploaded PDF.")

        return MarkdownDocument(filename=filename, markdown=markdown, characters=len(markdown))
