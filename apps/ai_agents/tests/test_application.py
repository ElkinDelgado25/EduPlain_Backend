import pytest

from apps.ai_agents.application.use_cases import (
    MARKDOWN_PREVIEW_MAX_CHARS,
    AnalyzeSyllabusPdf,
    SyllabusAnalysisError,
)
from apps.ai_agents.domain.entities import SyllabusAnalysisDraft
from apps.ai_agents.infrastructure.generic_syllabus_analyzer import (
    GENERIC_NOTES,
    GENERIC_OBJECTIVE,
    GenericSyllabusAnalyzer,
)
from apps.documents.application.use_cases import EmptyDocumentError
from apps.documents.domain.entities import MarkdownDocument


class InMemoryMarkdownConverter:
    def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
        markdown = "# Unidad 1\n\nFunciones y limites"
        return MarkdownDocument(filename=filename, markdown=markdown, characters=len(markdown))


class InMemorySyllabusAnalyzer:
    @property
    def version(self) -> str:
        return "test-v1"

    def analyze(self, *, filename: str, markdown: str) -> SyllabusAnalysisDraft:
        return SyllabusAnalysisDraft(
            course_name="Calculo",
            general_objective="Objetivo de prueba",
            units=(),
            confidence="test",
            notes=f"Analizado {filename} con {len(markdown)} caracteres",
        )


def test_analyze_syllabus_pdf_returns_generic_phase_one_result() -> None:
    result = AnalyzeSyllabusPdf(
        converter=InMemoryMarkdownConverter(),
        analyzer=GenericSyllabusAnalyzer(),
    ).execute(filename="silabo.pdf", content=b"pdf-content")

    assert result.status == "completed"
    assert result.filename == "silabo.pdf"
    assert result.characters_extracted == len("# Unidad 1\n\nFunciones y limites")
    assert result.markdown_preview == "# Unidad 1\n\nFunciones y limites"
    assert result.analysis.course_name is None
    assert result.analysis.general_objective == GENERIC_OBJECTIVE
    assert result.analysis.units == ()
    assert result.analysis.confidence == "generic"
    assert result.analysis.notes == GENERIC_NOTES
    assert result.phase == 1
    assert result.agent == "syllabus-analyzer"
    assert result.version == "generic-v1"
    assert result.steps_completed == (
        "pdf_received",
        "markdown_extracted",
        "analysis_generated",
    )


def test_analyze_syllabus_pdf_truncates_markdown_preview() -> None:
    long_markdown = "a" * (MARKDOWN_PREVIEW_MAX_CHARS + 50)

    class LongMarkdownConverter:
        def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
            return MarkdownDocument(
                filename=filename,
                markdown=long_markdown,
                characters=len(long_markdown),
            )

    result = AnalyzeSyllabusPdf(
        converter=LongMarkdownConverter(),
        analyzer=GenericSyllabusAnalyzer(),
    ).execute(filename="silabo.pdf", content=b"pdf-content")

    assert result.markdown_preview.endswith("...")
    assert len(result.markdown_preview) == MARKDOWN_PREVIEW_MAX_CHARS + 3


def test_analyze_syllabus_pdf_uses_injected_analyzer() -> None:
    result = AnalyzeSyllabusPdf(
        converter=InMemoryMarkdownConverter(),
        analyzer=InMemorySyllabusAnalyzer(),
    ).execute(filename="silabo.pdf", content=b"pdf-content")

    assert result.version == "test-v1"
    assert result.analysis.course_name == "Calculo"
    assert result.analysis.notes == (
        f"Analizado silabo.pdf con {len('# Unidad 1\n\nFunciones y limites')} caracteres"
    )


def test_analyze_syllabus_pdf_rejects_non_pdf_documents() -> None:
    with pytest.raises(SyllabusAnalysisError, match="Only PDF documents"):
        AnalyzeSyllabusPdf(
            converter=InMemoryMarkdownConverter(),
            analyzer=GenericSyllabusAnalyzer(),
        ).execute(filename="silabo.txt", content=b"plain-text")


def test_analyze_syllabus_pdf_rejects_empty_documents() -> None:
    with pytest.raises(SyllabusAnalysisError, match="empty"):
        AnalyzeSyllabusPdf(
            converter=InMemoryMarkdownConverter(),
            analyzer=GenericSyllabusAnalyzer(),
        ).execute(filename="silabo.pdf", content=b"")


def test_analyze_syllabus_pdf_wraps_document_conversion_errors() -> None:
    class FailingConverter:
        def convert(self, *, filename: str, content: bytes) -> MarkdownDocument:
            raise EmptyDocumentError("The uploaded PDF is empty.")

    with pytest.raises(SyllabusAnalysisError, match="empty"):
        AnalyzeSyllabusPdf(
            converter=FailingConverter(),
            analyzer=GenericSyllabusAnalyzer(),
        ).execute(filename="silabo.pdf", content=b"pdf-content")


def test_analyze_syllabus_pdf_wraps_unsupported_document_error() -> None:
    with pytest.raises(SyllabusAnalysisError, match="Only PDF documents"):
        AnalyzeSyllabusPdf(
            converter=InMemoryMarkdownConverter(),
            analyzer=GenericSyllabusAnalyzer(),
        ).execute(filename="silabo.txt", content=b"plain-text")
