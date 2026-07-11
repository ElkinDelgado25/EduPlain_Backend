import json
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from apps.ai_agents.application.use_cases import SyllabusAnalysisError
from apps.ai_agents.domain.entities import (
    SyllabusAnalysisDraft,
    SyllabusTopicDraft,
    SyllabusUnitDraft,
)

SYSTEM_PROMPT = (
    "Eres un asistente académico que analiza sílabos universitarios en español. "
    "Responde únicamente con JSON válido siguiendo el esquema solicitado. "
    "Extrae información real del texto proporcionado. "
    "Si un dato no aparece en el sílabo, usa null para course_name o general_objective "
    "y una lista vacía para units."
)

USER_PROMPT_TEMPLATE = (
    "Analiza el siguiente sílabo universitario extraído del archivo {filename}.\n\n"
    "Devuelve JSON con esta forma exacta:\n"
    "{{\n"
    '  "course_name": string | null,\n'
    '  "general_objective": string | null,\n'
    '  "units": [\n'
    "    {{\n"
    '      "number": number,\n'
    '      "title": string,\n'
    '      "topics": [\n'
    '        {{"title": string, "subtopics": [string]}}\n'
    "      ]\n"
    "    }}\n"
    "  ],\n"
    '  "notes": string\n'
    "}}\n\n"
    "Contenido del sílabo:\n\n{markdown}"
)


class OpenAISyllabusAnalyzer:
    @property
    def version(self) -> str:
        return "ai-v1"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_input_chars: int,
        client: OpenAI | None = None,
    ) -> None:
        self.model = model
        self.max_input_chars = max_input_chars
        self._client = client or OpenAI(api_key=api_key)

    def analyze(self, *, filename: str, markdown: str) -> SyllabusAnalysisDraft:
        prompt_markdown, truncated = _truncate_markdown(markdown, self.max_input_chars)
        user_prompt = USER_PROMPT_TEMPLATE.format(filename=filename, markdown=prompt_markdown)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except RateLimitError as exc:
            raise SyllabusAnalysisError(
                "The syllabus AI service reached its rate limit. Try again later."
            ) from exc
        except APITimeoutError as exc:
            raise SyllabusAnalysisError(
                "The syllabus AI service timed out while analyzing the document."
            ) from exc
        except APIError as exc:
            raise SyllabusAnalysisError(
                "The syllabus AI service could not complete the analysis."
            ) from exc

        raw_content = _extract_response_content(response)
        try:
            payload = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise SyllabusAnalysisError(
                "The syllabus AI service returned an invalid analysis payload."
            ) from exc

        notes = _optional_string(payload.get("notes")) or ""
        if truncated:
            truncation_note = (
                f"El texto enviado al modelo fue truncado a {self.max_input_chars} caracteres."
            )
            notes = f"{notes} {truncation_note}".strip()

        return SyllabusAnalysisDraft(
            course_name=_optional_string(payload.get("course_name")),
            general_objective=_optional_string(payload.get("general_objective")),
            units=_parse_units(payload.get("units")),
            confidence="ai",
            notes=notes,
        )


def _truncate_markdown(markdown: str, max_input_chars: int) -> tuple[str, bool]:
    normalized = markdown.strip()
    if len(normalized) <= max_input_chars:
        return normalized, False
    return normalized[:max_input_chars].rstrip(), True


def _extract_response_content(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise SyllabusAnalysisError(
            "The syllabus AI service returned an empty analysis payload."
        ) from exc

    if not isinstance(content, str) or not content.strip():
        raise SyllabusAnalysisError("The syllabus AI service returned an empty analysis payload.")
    return content


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_units(raw_units: Any) -> tuple[SyllabusUnitDraft, ...]:
    if not isinstance(raw_units, list):
        return ()

    units: list[SyllabusUnitDraft] = []
    for index, raw_unit in enumerate(raw_units, start=1):
        if not isinstance(raw_unit, dict):
            continue

        title = _optional_string(raw_unit.get("title"))
        if title is None:
            continue

        number_value = raw_unit.get("number", index)
        number = number_value if isinstance(number_value, int) and number_value > 0 else index
        topics = _parse_topics(raw_unit.get("topics"))
        units.append(SyllabusUnitDraft(number=number, title=title, topics=topics))

    return tuple(units)


def _parse_topics(raw_topics: Any) -> tuple[SyllabusTopicDraft, ...]:
    if not isinstance(raw_topics, list):
        return ()

    topics: list[SyllabusTopicDraft] = []
    for raw_topic in raw_topics:
        if not isinstance(raw_topic, dict):
            continue

        title = _optional_string(raw_topic.get("title"))
        if title is None:
            continue

        subtopics = _parse_subtopics(raw_topic.get("subtopics"))
        topics.append(SyllabusTopicDraft(title=title, subtopics=subtopics))

    return tuple(topics)


def _parse_subtopics(raw_subtopics: Any) -> tuple[str, ...]:
    if not isinstance(raw_subtopics, list):
        return ()

    subtopics: list[str] = []
    for raw_subtopic in raw_subtopics:
        if not isinstance(raw_subtopic, str):
            continue
        stripped = raw_subtopic.strip()
        if stripped:
            subtopics.append(stripped)
    return tuple(subtopics)
