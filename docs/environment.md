# Variables de entorno

La configuración sigue los principios de Twelve-Factor App: los valores operativos y secretos se reciben desde el entorno. `.env.example` documenta valores locales y puede copiarse como `.env`; el archivo real está ignorado por Git.

| Variable | Requerida en producción | Ejemplo | Descripción |
|---|---:|---|---|
| `DJANGO_SECRET_KEY` | Sí | `replace-with-a-secret` | Firma criptográfica de Django. |
| `DJANGO_DEBUG` | Sí | `False` | Activa o desactiva modo debug. |
| `DJANGO_ALLOWED_HOSTS` | Sí | `api.example.edu` | Hosts separados por comas. |
| `DJANGO_ENVIRONMENT` | Sí | `production` | Nombre informativo del entorno. |
| `DJANGO_SETTINGS_MODULE` | Sí | `config.settings.production` | Módulo de configuración que carga Django. |
| `DJANGO_SUPERUSER_USERNAME` | No | `elkin` | Usuario del bootstrap administrativo. |
| `DJANGO_SUPERUSER_EMAIL` | No | `elkindelgado05@gmail.com` | Correo del bootstrap administrativo. |
| `DJANGO_SUPERUSER_FULL_NAME` | No | `Elkin Delgado` | Nombre completo requerido por `users.User`. |
| `DJANGO_SUPERUSER_PASSWORD` | No | Sin valor | Secreto requerido únicamente para crear la cuenta inicial. |
| `POSTGRES_DB` | Sí | `academic_db` | Base de datos. |
| `POSTGRES_USER` | Sí | `academic_user` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Sí | `strong-secret` | Contraseña de PostgreSQL. |
| `POSTGRES_HOST` | Sí | `localhost` | Host de PostgreSQL para Django ejecutado localmente. |
| `POSTGRES_PORT` | Sí | `55432` | Puerto publicado por Docker para Django local. |

## Uso con Docker Compose

Compose lee automáticamente un `.env` ubicado junto a `docker-compose.yml` y usa sus valores en la interpolación. El servicio `api` reemplaza la conexión por `POSTGRES_HOST=db` y `POSTGRES_PORT=5432`, los valores internos de PostgreSQL. Para levantar únicamente la base de datos y ejecutar Django desde el host, use `docker compose up -d db` y conserve `POSTGRES_HOST=localhost` y `POSTGRES_PORT=55432`.

## Uso local de Django

`config.settings.development` carga automáticamente el archivo `.env` de la raíz. Las variables ya definidas en el proceso tienen prioridad, por lo que CI, Docker y la terminal pueden sobrescribir los valores locales cuando sea necesario.

Producción no carga `.env` automáticamente y continúa dependiendo exclusivamente del entorno. También puede sobrescribir valores de desarrollo individualmente desde PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "local-secret"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:DJANGO_ENVIRONMENT = "development"
$env:DJANGO_SETTINGS_MODULE = "config.settings.development"
$env:POSTGRES_DB = "academic_db"
$env:POSTGRES_USER = "academic_user"
$env:POSTGRES_PASSWORD = "academic_password"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "55432"
python manage.py runserver
```

## Superusuario inicial

El comando `python manage.py bootstrap_superuser` utiliza las variables `DJANGO_SUPERUSER_*`. Es idempotente: si el usuario ya es superusuario, termina correctamente sin cambiar su contraseña. Si existe como usuario normal, se detiene para evitar una elevación de privilegios accidental.

`DJANGO_SUPERUSER_PASSWORD` nunca debe versionarse. El valor `CHANGE_ME` se rechaza explícitamente.

### Recomendación por entorno

- **Local:** ejecutar el comando manualmente con una contraseña temporal en `.env`; eliminar el valor después de crear la cuenta.
- **Staging:** inyectar las variables desde el gestor de secretos y ejecutar el comando como tarea idempotente durante el despliegue.
- **Producción:** ejecutar el comando como una tarea única y auditable después de las migraciones. No crear administradores mediante señales, imports ni migraciones de datos, y no conservar la contraseña bootstrap como variable permanente del servicio web.

## Producción

No use los valores predeterminados de desarrollo. Genere una clave larga, mantenga `DJANGO_DEBUG=False`, limite `DJANGO_ALLOWED_HOSTS`, seleccione `config.settings.production` y administre secretos con el mecanismo seguro de la plataforma de despliegue.
