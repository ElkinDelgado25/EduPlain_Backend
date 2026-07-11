from apps.ai_agents.application.use_cases import PHASE_1_VERSION
from apps.ai_agents.domain.entities import SyllabusAnalysisDraft

GENERIC_OBJECTIVE = (
    "Recibimos tu sílabo y extrajimos su contenido correctamente. "
    "En esta fase inicial aún no generamos la ruta de aprendizaje estructurada; "
    "el análisis detallado con inteligencia artificial llegará en la siguiente fase."
)

GENERIC_NOTES = (
    f"Respuesta genérica de la fase 1 ({PHASE_1_VERSION}). "
    "La estructura de unidades y temas se completará cuando el agente académico esté activo."
)


class GenericSyllabusAnalyzer:
    @property
    def version(self) -> str:
        return PHASE_1_VERSION

    def analyze(self, *, filename: str, markdown: str) -> SyllabusAnalysisDraft:
        del filename  # reservado para futuras heurísticas o prompts con contexto de archivo
        del markdown  # reservado para futura extracción con LLM

        return SyllabusAnalysisDraft(
            course_name=None,
            general_objective=GENERIC_OBJECTIVE,
            units=(),
            confidence="generic",
            notes=GENERIC_NOTES,
        )
