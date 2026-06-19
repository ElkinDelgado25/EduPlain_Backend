# Settings por entorno

`base.py` define componentes compartidos, base de datos, DRF y OpenAPI. `development.py` habilita herramientas cómodas para desarrollo. `production.py` fuerza opciones seguras básicas. `test.py` usa SQLite para pruebas aisladas y reproducibles.

Seleccione el entorno con `DJANGO_SETTINGS_MODULE`:

- `config.settings.development`
- `config.settings.production`
- `config.settings.test`

`DJANGO_ENVIRONMENT` es el nombre informativo mostrado por health; no selecciona automáticamente el módulo de settings.
