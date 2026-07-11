# Feature AI Agents

Orquesta capacidades de inteligencia artificial para Eduplain. La fase 1 recibe un sílabo en PDF, extrae su contenido como Markdown y devuelve un análisis estructurado.

Capas:

- `domain`: borradores de análisis y resultado de la fase 1.
- `application`: caso de uso `AnalyzeSyllabusPdf` y puerto `SyllabusAnalyzer`.
- `infrastructure`: analizador genérico, adaptador OpenAI y factory de selección.
- `interfaces`: contrato HTTP autenticado para cargar sílabos.

## Modos de análisis

| Condición | Adaptador | `version` | `confidence` |
|---|---|---|---|
| `AI_SYLLABUS_ENABLED=false` o sin `OPENAI_API_KEY` | `GenericSyllabusAnalyzer` | `generic-v1` | `generic` |
| IA activa y key configurada | `OpenAISyllabusAnalyzer` | `ai-v1` | `ai` |

Variables de entorno: ver `docs/environment.md`.

El endpoint reutiliza la conversión PDF→Markdown del módulo `documents` sin acoplar dominio a infraestructura ajena.
