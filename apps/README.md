# Módulos de negocio

`apps/` agrupa el sistema por capacidades funcionales, no por tipos técnicos globales. Cada feature es responsable de su modelo, casos de uso, adaptadores y contratos HTTP.

Los módulos actuales son:

- `documents`: procesamiento documental para convertir PDFs académicos en Markdown.
- `health`: estado operativo del servicio.
- `users`: directorio académico y base para identidad futura.

Una feature nueva debe depender lo mínimo posible de otras features. La coordinación transversal debe expresarse mediante contratos de aplicación, no mediante imports directos de modelos ORM ajenos.
