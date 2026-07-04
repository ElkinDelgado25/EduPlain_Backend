# Claude Code — Eduplain Backend

Backend Django REST para una plataforma académica universitaria. Arquitectura modular (domain / application / infrastructure / interfaces) con PostgreSQL y orquestación local vía Aspire.

## Guía completa

Lea [`AGENTS.md`](AGENTS.md) para arquitectura, seguridad, calidad y control de versiones.

## Resolver un issue

```powershell
gh issue view <N> --repo ElkinDelgado25/EduPlain_Backend
git checkout dev
git pull origin dev
# implementar en dev
# gh pr create --base main --head dev --title "fix: ..." --body "Closes #N"
```

Flujo de ramas: **issue → commit en `dev` → PR `dev` → `main` → sync `dev`**. No crear ramas auxiliares por issue.

## Levantar el backend (Aspire)

```powershell
docker compose down
dotnet build .\aspire\Eduplain.AppHost\Eduplain.AppHost.csproj
aspire run --apphost .\aspire\Eduplain.AppHost
```

Pre-requisitos: `.venv` activo, `.env` con secretos locales. Detalles en [`docs/aspire.md`](docs/aspire.md).

## Validar antes de cerrar

Checklist del agente (sin pytest):

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate --file schema.yml
python -m ruff check .
python -m ruff format --check .
docker compose config --quiet
```

PostgreSQL debe estar activo para el check de migraciones. Ejecutar `python -m pytest` solo si el usuario lo pide explícitamente.

## Git

- No commitear ni pushear salvo petición explícita del usuario.
- Plantillas de issue y PR en `.github/`.
