# Feature Documents

Gestiona capacidades de procesamiento documental para Eduplain. Su primer caso de uso convierte un PDF de silabo en Markdown para validar la calidad del texto antes de construir rutas de aprendizaje.

Capas:

- `domain`: resultados y tipos propios del procesamiento documental.
- `application`: caso de uso y puerto de conversion.
- `infrastructure`: adaptador concreto basado en `pymupdf4llm`.
- `interfaces`: contrato HTTP para carga de PDF y respuesta Markdown.

El endpoint inicial requiere autenticacion por la politica global del backend. No debe exponerse como publico hasta definir autenticacion institucional y limites operativos.
