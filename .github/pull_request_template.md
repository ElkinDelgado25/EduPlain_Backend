## Resumen

<!-- Qué cambia y por qué -->

Closes #

## Ramas

- **Head:** `dev` (donde se resolvió el issue)
- **Base:** `main` (destino tras revisión)

## Checklist

- [ ] Leí el issue y cumplí los criterios de aceptación
- [ ] `python manage.py check`
- [ ] `python manage.py makemigrations --check --dry-run` (con PostgreSQL activo)
- [ ] `python manage.py spectacular --validate --file schema.yml`
- [ ] `python -m pytest` (opcional; ejecutar solo si el autor lo indica o el revisor lo pide)
- [ ] `python -m ruff check .`
- [ ] `python -m ruff format --check .`
- [ ] `docker compose config --quiet`
- [ ] Documentación/OpenAPI actualizados si aplica

## Notas para revisión

<!-- Decisiones de diseño, riesgos, capturas, pasos manuales de prueba -->
