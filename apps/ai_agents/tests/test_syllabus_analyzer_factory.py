from django.test import override_settings

from apps.ai_agents.infrastructure.generic_syllabus_analyzer import GenericSyllabusAnalyzer
from apps.ai_agents.infrastructure.openai_syllabus_analyzer import OpenAISyllabusAnalyzer
from apps.ai_agents.infrastructure.syllabus_analyzer_factory import get_syllabus_analyzer


@override_settings(AI_SYLLABUS_ENABLED=False, OPENAI_API_KEY="")
def test_get_syllabus_analyzer_returns_generic_when_ai_disabled() -> None:
    analyzer = get_syllabus_analyzer()

    assert isinstance(analyzer, GenericSyllabusAnalyzer)
    assert analyzer.version == "generic-v1"


@override_settings(AI_SYLLABUS_ENABLED=True, OPENAI_API_KEY="")
def test_get_syllabus_analyzer_returns_generic_when_api_key_missing() -> None:
    analyzer = get_syllabus_analyzer()

    assert isinstance(analyzer, GenericSyllabusAnalyzer)


@override_settings(
    AI_SYLLABUS_ENABLED=True,
    OPENAI_API_KEY="sk-test-key",
    AI_SYLLABUS_MODEL="gpt-4o-mini",
    AI_SYLLABUS_MAX_INPUT_CHARS=12000,
)
def test_get_syllabus_analyzer_returns_openai_when_enabled() -> None:
    analyzer = get_syllabus_analyzer()

    assert isinstance(analyzer, OpenAISyllabusAnalyzer)
    assert analyzer.version == "ai-v1"
    assert analyzer.model == "gpt-4o-mini"
    assert analyzer.max_input_chars == 12000
