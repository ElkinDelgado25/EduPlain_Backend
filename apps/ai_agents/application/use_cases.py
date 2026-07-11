from typing import Protocol

from apps.ai_agents.domain.entities import SyllabusAnalysisDraft, SyllabusAnalysisResult
from apps.documents.application.use_cases import (
    ConvertPdfToMarkdown,
    DocumentConversionError,
    MarkdownConverter,
)

MARKDOWN_PREVIEW_MAX_CHARS = 500
PHASE_1_AGENT = "syllabus-analyzer"
PHASE_1_VERSION = "generic-v1"


class SyllabusAnalysisError(Exception):
    """Raised when a syllabus cannot be analyzed."""


class SyllabusAnalyzer(Protocol):
    @property
    def version(self) -> str: ...

    def analyze(self, *, filename: str, markdown: str) -> SyllabusAnalysisDraft: ...


class AnalyzeSyllabusPdf:
    def __init__(
        self,
        converter: MarkdownConverter,
        analyzer: SyllabusAnalyzer,
    ) -> None:
        self.converter = converter
        self.analyzer = analyzer

    def execute(self, *, filename: str, content: bytes) -> SyllabusAnalysisResult:
        try:
            markdown_document = ConvertPdfToMarkdown(self.converter).execute(
                filename=filename,
                content=content,
            )
        except DocumentConversionError as exc:
            raise SyllabusAnalysisError(str(exc)) from exc

        analysis = self.analyzer.analyze(
            filename=filename,
            markdown=markdown_document.markdown,
        )
        preview = _build_markdown_preview(markdown_document.markdown)

        return SyllabusAnalysisResult(
            status="completed",
            filename=markdown_document.filename,
            characters_extracted=markdown_document.characters,
            markdown_preview=preview,
            analysis=analysis,
            phase=1,
            agent=PHASE_1_AGENT,
            version=self.analyzer.version,
            steps_completed=(
                "pdf_received",
                "markdown_extracted",
                "analysis_generated",
            ),
        )


def _build_markdown_preview(markdown: str) -> str:
    normalized = markdown.strip()
    if len(normalized) <= MARKDOWN_PREVIEW_MAX_CHARS:
        return normalized
    return f"{normalized[:MARKDOWN_PREVIEW_MAX_CHARS].rstrip()}..."
