import json
from types import SimpleNamespace

import pytest
from openai import APIError

from apps.ai_agents.application.use_cases import SyllabusAnalysisError
from apps.ai_agents.infrastructure.openai_syllabus_analyzer import OpenAISyllabusAnalyzer


class FakeCompletions:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.last_kwargs: dict | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        content = json.dumps(self.payload)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class FakeOpenAIClient:
    def __init__(self, payload: dict) -> None:
        self.completions = FakeCompletions(payload)
        self.chat = SimpleNamespace(completions=self.completions)


def test_openai_syllabus_analyzer_parses_structured_response() -> None:
    payload = {
        "course_name": "Calculo Diferencial",
        "general_objective": "Comprender limites y derivadas.",
        "units": [
            {
                "number": 1,
                "title": "Funciones",
                "topics": [
                    {"title": "Dominio", "subtopics": ["Imagen", "Graficas"]},
                ],
            }
        ],
        "notes": "Analisis inicial del silabo.",
    }
    client = FakeOpenAIClient(payload)
    analyzer = OpenAISyllabusAnalyzer(
        api_key="test-key",
        model="gpt-4o-mini",
        max_input_chars=24000,
        client=client,
    )

    result = analyzer.analyze(filename="silabo.pdf", markdown="# Unidad 1\n\nFunciones")

    assert result.course_name == "Calculo Diferencial"
    assert result.general_objective == "Comprender limites y derivadas."
    assert len(result.units) == 1
    assert result.units[0].title == "Funciones"
    assert result.units[0].topics[0].subtopics == ("Imagen", "Graficas")
    assert result.confidence == "ai"
    assert result.notes == "Analisis inicial del silabo."
    assert client.completions.last_kwargs["model"] == "gpt-4o-mini"


def test_openai_syllabus_analyzer_truncates_long_markdown_and_notes_it() -> None:
    client = FakeOpenAIClient(
        {
            "course_name": "Algebra",
            "general_objective": "Objetivo",
            "units": [],
            "notes": "",
        }
    )
    analyzer = OpenAISyllabusAnalyzer(
        api_key="test-key",
        model="gpt-4o-mini",
        max_input_chars=20,
        client=client,
    )

    result = analyzer.analyze(filename="silabo.pdf", markdown="a" * 100)

    assert "truncado a 20 caracteres" in result.notes
    user_prompt = client.completions.last_kwargs["messages"][1]["content"]
    assert "a" * 20 in user_prompt
    assert "a" * 100 not in user_prompt


def test_openai_syllabus_analyzer_rejects_invalid_json_payload() -> None:
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="not-json"))]
                )
            )
        )
    )
    analyzer = OpenAISyllabusAnalyzer(
        api_key="test-key",
        model="gpt-4o-mini",
        max_input_chars=24000,
        client=client,
    )

    with pytest.raises(SyllabusAnalysisError, match="invalid analysis payload"):
        analyzer.analyze(filename="silabo.pdf", markdown="# Unidad 1")


def test_openai_syllabus_analyzer_wraps_api_errors() -> None:
    class FailingCompletions:
        def create(self, **kwargs):
            raise APIError("upstream failure", request=SimpleNamespace(), body=None)

    analyzer = OpenAISyllabusAnalyzer(
        api_key="test-key",
        model="gpt-4o-mini",
        max_input_chars=24000,
        client=SimpleNamespace(chat=SimpleNamespace(completions=FailingCompletions())),
    )

    with pytest.raises(SyllabusAnalysisError, match="could not complete"):
        analyzer.analyze(filename="silabo.pdf", markdown="# Unidad 1")
