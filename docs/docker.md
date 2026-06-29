# Docker

## Servicios

`docker-compose.yml` define:

- `db`: PostgreSQL con volumen persistente y health check.
- `api`: aplicación Django de Eduplain expuesta en el puerto `8000`.

PostgreSQL publica el puerto `55432` del host hacia su puerto interno `5432` para que Django pueda ejecutarse desde el entorno virtual sin interferir con otras instalaciones locales de PostgreSQL. Cuando se utiliza el stack completo, la API espera a PostgreSQL, ejecuta migraciones, intenta el bootstrap opcional del superusuario y luego inicia el servidor de desarrollo.

## Solo PostgreSQL para desarrollo local

El flujo local recomendado es Aspire; use Compose solo cuando quiera probar explícitamente este camino alternativo. No ejecute Compose y Aspire al mismo tiempo para el mismo backend, porque Compose levanta `eduplain-backend-db-1` y Aspire levanta su propio PostgreSQL.

Este es el flujo alternativo cuando Django se ejecuta desde `.venv` sin Aspire:

```powershell
docker compose up -d db
docker compose ps
```

En `.env`, use `POSTGRES_HOST=localhost` y `POSTGRES_PORT=55432`. La configuración de desarrollo carga ese archivo automáticamente; ejecute `python manage.py migrate` y `python manage.py runserver` desde el host.

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

### Bootstrap opcional del superusuario

Defina las variables `EDUPLAIN_BOOTSTRAP_ADMIN_*` en `.env` para que el stack completo cree el superusuario inicial después de migrar. El comando no cambia cuentas existentes y omite la creación cuando la contraseña está vacía:

```powershell
docker compose exec api python manage.py bootstrap_superuser
```

No incorpore la contraseña en la imagen ni en `docker-compose.yml`. En staging y producción, inyecte la identidad y la contraseña desde el gestor de secretos/configuración de la plataforma y ejecute el comando como una tarea única controlada.

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
