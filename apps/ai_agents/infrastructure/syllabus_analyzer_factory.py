from django.conf import settings

from apps.ai_agents.infrastructure.generic_syllabus_analyzer import GenericSyllabusAnalyzer
from apps.ai_agents.infrastructure.openai_syllabus_analyzer import OpenAISyllabusAnalyzer


def get_syllabus_analyzer():
    api_key = settings.OPENAI_API_KEY.strip()
    if settings.AI_SYLLABUS_ENABLED and api_key:
        return OpenAISyllabusAnalyzer(
            api_key=api_key,
            model=settings.AI_SYLLABUS_MODEL,
            max_input_chars=settings.AI_SYLLABUS_MAX_INPUT_CHARS,
        )
    return GenericSyllabusAnalyzer()
