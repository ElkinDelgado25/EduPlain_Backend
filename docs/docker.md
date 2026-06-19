# Docker

## Servicios

`docker-compose.yml` define:

- `db`: PostgreSQL con volumen persistente y health check.
- `api`: aplicación Django de Eduplain expuesta en el puerto `8000`.

PostgreSQL publica el puerto `55432` del host hacia su puerto interno `5432` para que Django pueda ejecutarse desde el entorno virtual sin interferir con otras instalaciones locales de PostgreSQL. La API espera a que PostgreSQL esté saludable, ejecuta migraciones y luego inicia el servidor de desarrollo cuando se utiliza el stack completo.

## Solo PostgreSQL para desarrollo local

Este es el flujo recomendado cuando Django se ejecuta desde `.venv`:

```powershell
docker compose up -d db
docker compose ps
```

En `.env`, use `POSTGRES_HOST=localhost` y `POSTGRES_PORT=55432`. Después cargue las variables en PowerShell y ejecute `python manage.py migrate` y `python manage.py runserver` desde el host.

## Stack completo

```bash
docker compose up --build
```

El stack exige `.env` para impedir que valores inseguros se utilicen por omisión:

```powershell
Copy-Item .env.example .env
# Reemplace DJANGO_SECRET_KEY y POSTGRES_PASSWORD antes de iniciar.
docker compose up --build
```

Aunque `.env` utiliza `POSTGRES_HOST=localhost` y `POSTGRES_PORT=55432` para el proceso local, Compose configura `POSTGRES_HOST=db` y `POSTGRES_PORT=5432` dentro del contenedor `api`.

## Comandos útiles

```bash
docker compose ps
docker compose logs -f db
docker compose logs -f api
docker compose exec api python manage.py check
docker compose exec api python manage.py createsuperuser
docker compose down
```

Para eliminar también los datos locales de PostgreSQL:

```bash
docker compose down -v
```

Este último comando elimina el volumen y no debe utilizarse si se necesitan conservar los datos.

## Imagen

El `Dockerfile` usa la imagen oficial `python:3.13.13-slim-bookworm`, instala dependencias fijadas, ejecuta con un usuario sin privilegios y declara Gunicorn como comando predeterminado. Compose reemplaza ese comando por `runserver` para desarrollo y monta el código como volumen.

En un despliegue real, no monte el código, ejecute migraciones como una tarea controlada y use el comando Gunicorn de la imagen. Configure además proxy TLS, observabilidad, backups y gestión segura de secretos.

Para Amazon ECR/ECS o App Runner, construya y publique esta imagen en lugar de depender del Python instalado en el host. El tag fija Python 3.13.13 y Debian Bookworm; las actualizaciones de runtime deben realizarse como cambios explícitos, seguidos por una reconstrucción y las validaciones del repositorio.
