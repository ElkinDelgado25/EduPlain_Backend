from dataclasses import dataclass


@dataclass(frozen=True)
class SyllabusTopicDraft:
    title: str
    subtopics: tuple[str, ...]


@dataclass(frozen=True)
class SyllabusUnitDraft:
    number: int
    title: str
    topics: tuple[SyllabusTopicDraft, ...]


@dataclass(frozen=True)
class SyllabusAnalysisDraft:
    course_name: str | None
    general_objective: str | None
    units: tuple[SyllabusUnitDraft, ...]
    confidence: str
    notes: str


@dataclass(frozen=True)
class SyllabusAnalysisResult:
    status: str
    filename: str
    characters_extracted: int
    markdown_preview: str
    analysis: SyllabusAnalysisDraft
    phase: int
    agent: str
    version: str
    steps_completed: tuple[str, ...]
