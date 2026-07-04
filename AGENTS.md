# Guía para asistentes de IA y desarrolladores

## Propósito

Este repositorio prioriza una arquitectura clara y educativa. Todo cambio debe conservar la separación entre dominio, casos de uso, infraestructura e interfaces.

## Reglas de arquitectura

1. Organizar capacidades nuevas como features dentro de `apps/`.
2. Mantener `domain/` libre de imports de Django, DRF, bases de datos y HTTP.
3. Definir la orquestación y los puertos en `application/`.
4. Implementar ORM, repositorios y servicios externos en `infrastructure/`.
5. Limitar vistas, serializadores y URL routing a `interfaces/`.
6. Hacer que las dependencias apunten hacia el dominio, nunca desde el dominio hacia frameworks.
7. No acceder al ORM directamente desde un caso de uso.

## Reglas de API y seguridad

- No agregar login, JWT ni CRUD completo hasta que el alcance lo solicite.
- Mantener `health` y `users/public` como rutas públicas explícitas.
- Los endpoints nuevos heredan el permiso global autenticado salvo decisión documentada.
- Usar serializadores de salida explícitos para evitar fugas de campos sensibles.
- Nunca devolver contraseñas, hashes, tokens, flags administrativos o permisos.
- Documentar cada endpoint nuevo en OpenAPI y `docs/endpoints.md`.

## Configuración

- Ejecutar el proyecto únicamente con CPython 3.13.13 o un parche posterior de la rama 3.13; no usar `3.13t` free-threaded.
- Mantener sincronizados `Dockerfile`, `.python-version`, README y el guard de runtime al actualizar Python.
- Fijar dependencias de producción con versiones exactas para conservar builds reproducibles.
- Leer secretos y valores variables desde el entorno.
- Agregar variables nuevas a `.env.example` y `docs/environment.md`.
- No versionar `.env`, credenciales reales ni datos personales.
- Mantener separados los ajustes de desarrollo y producción.

## Flujo de issues y ramas

Los issues viven en GitHub (`ElkinDelgado25/EduPlain_Backend`). Los agentes deben leerlos con `gh issue view <N>` antes de implementar.

```text
GitHub Issue → commit en dev → PR dev → main → sync dev
```

- Rama de trabajo única: **`dev`** (no crear ramas por issue salvo petición explícita).
- Implementar cada fix directamente en `dev` tras `git pull origin dev`.
- Abrir PR de revisión **`dev` → `main`**: `gh pr create --base main --head dev --body "Closes #N"`.
- Referenciar el issue en commit y PR con `Closes #N`.
- Tras merge a `main`, sincronizar `dev` desde `main`.
- Plantillas: `.github/ISSUE_TEMPLATE/` y `.github/pull_request_template.md`.
- Reglas Cursor detalladas: `.cursor/rules/issue-workflow.mdc` y `.cursor/rules/local-dev-ops.mdc`.

## Orquestación local

El flujo local principal usa **Aspire**. No ejecutar Compose y Aspire al mismo tiempo.

```powershell
docker compose down
dotnet build .\aspire\Eduplain.AppHost\Eduplain.AppHost.csproj
aspire run --apphost .\aspire\Eduplain.AppHost
```

- Django expone `http://localhost:8000`; PostgreSQL de Aspire en `localhost:55433`.
- Aspire reutiliza `.venv` si existe; el intérprete debe ser CPython `3.13.13+`.
- `config.settings.development` carga `.env` y luego `.env.local` sin reemplazar variables ya definidas en el proceso.
- Consulte `docs/aspire.md` para recursos orquestados y versiones fijadas.

**Alternativa: Django en `.venv` + solo PostgreSQL con Compose** (cuando no se use Aspire):

```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d db
python manage.py migrate
python manage.py runserver
```

- PostgreSQL de Compose se publica en `localhost:55432`.
- Los comandos locales de Django deben ejecutarse con el entorno virtual activo.

**Stack completo en Docker** (solo cuando la tarea lo pida explícitamente):

```powershell
docker compose up --build
docker compose exec api python manage.py <comando>
```

## Calidad y entrega

### Checklist del agente

Validaciones automáticas al cerrar una tarea (sin pytest):

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate --file schema.yml
python -m ruff check .
python -m ruff format --check .
docker compose config --quiet
```

No ejecutar `python -m pytest` salvo petición explícita del usuario.

### Checklist completo de entrega

Para desarrolladores humanos o cuando el usuario pida validación total, añadir:

```bash
python -m pytest
```

Agregar pruebas cuando aparezca lógica condicional o reglas de negocio. Mantener comentarios centrados en el porqué; los nombres deben explicar el qué.

## Control de versiones

- No incluir `.env`, `.venv`, cachés, cobertura, credenciales ni datos generados localmente.
- Sí versionar `.env.example`, migraciones de Django, archivos `__init__.py`, documentación y configuración reproducible.
- Revisar `git status` antes de preparar un commit.
- Mantener cada commit enfocado en una sola intención y usar mensajes descriptivos.
- No reescribir ni descartar cambios ajenos o no relacionados con la tarea actual.

## Documentación

Actualizar el README del módulo cuando cambie su responsabilidad. Las decisiones transversales deben registrarse en `docs/architecture.md`; los detalles operativos pertenecen a `docs/docker.md` o `docs/environment.md`.

- Actualizar `docs/endpoints.md` y OpenAPI al crear o modificar endpoints.
- Actualizar `.env.example` y `docs/environment.md` al agregar o cambiar variables.
- Actualizar `docs/docker.md` cuando cambien servicios, puertos, volúmenes o comandos de contenedores.
- Documentar en el README cualquier cambio que afecte la instalación o el flujo inicial.
