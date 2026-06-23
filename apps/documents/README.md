# Feature Documents

Gestiona capacidades de procesamiento documental para Eduplain. Su primer caso de uso convierte un PDF de silabo en Markdown para validar la calidad del texto antes de construir rutas de aprendizaje.

También expone una base inicial para guardar y consultar PDFs. El adaptador actual usa filesystem local y un catálogo JSON; la aplicación depende de un puerto de almacenamiento para poder reemplazarlo después por MongoDB, S3, OneDrive u otro backend externo.

Capas:

- `domain`: resultados y tipos propios del procesamiento documental.
- `application`: caso de uso y puerto de conversion.
- `infrastructure`: adaptadores concretos basados en `pymupdf4llm` y storage local.
- `interfaces`: contrato HTTP para carga de PDF y respuesta Markdown.

El endpoint inicial requiere autenticacion por la politica global del backend. No debe exponerse como publico hasta definir autenticacion institucional y limites operativos.
