# Eduplain Backend

Backend de Eduplain para una plataforma académica universitaria, construido con Django REST Framework, PostgreSQL y una organización modular inspirada en DDD y Clean Architecture.

Runtime oficial: **CPython 3.13.13 o un parche posterior de la rama 3.13**. La versión está fijada en Docker y en `.python-version`; el proyecto rechaza intérpretes anteriores o de otra rama para evitar diferencias entre desarrollo y producción. No use builds `3.13t` free-threaded; el runtime validado es CPython estándar.

## Alcance actual

- Comprobación pública de salud del servicio.
- Directorio público de usuarios con una salida limitada a `id`, `full_name`, `email` y `role`.
- Contrato OpenAPI y Swagger UI.
- PostgreSQL y entorno local reproducible con Docker Compose.
- Modelo de usuario propio preparado para autenticación futura, sin implementar login ni JWT.

## Inicio rápido: Django local y PostgreSQL en Docker

El flujo recomendado para desarrollo mantiene Django en el entorno virtual local y ejecuta únicamente PostgreSQL en Docker.

Compruebe primero que el intérprete local sea compatible:

```powershell
python --version
# Python 3.13.13
py -3.13 --version
# Python 3.13.13
```

Si `py -3.13` resuelve a una versión anterior a `3.13.13`, instale un parche más reciente de CPython 3.13 antes de crear el entorno virtual.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` y asigne valores locales a `DJANGO_SECRET_KEY` y `POSTGRES_PASSWORD`. Mantenga `POSTGRES_HOST=localhost` y `POSTGRES_PORT=55432`; se usa un puerto alto en el host para no interferir con instalaciones locales de PostgreSQL. Después levante solamente la base de datos:

```powershell
docker compose up -d db
```

La configuración de desarrollo carga `.env` automáticamente. Aplique las migraciones e inicie Django:

```powershell
python manage.py migrate
python manage.py runserver
```

Servicios disponibles:

| Recurso | URL |
|---|---|
| Health check | <http://localhost:8000/api/health/> |
| Usuarios públicos | <http://localhost:8000/api/users/public/> |
| Swagger UI | <http://localhost:8000/api/docs/> |
| Esquema OpenAPI | <http://localhost:8000/api/schema/> |

### Superusuario inicial opcional

Para una instalación nueva, configure temporalmente `EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD` en `.env` y ejecute:

```powershell
python manage.py bootstrap_superuser
```

El comando crea `eduplain_su_owner` con correo técnico `owner@eduplain.local`, nombre `Eduplain System Owner`, rol `administrator` y visibilidad pública desactivada. Si la cuenta ya existe como superusuario, no cambia su contraseña. Acceda al panel en <http://localhost:8000/admin/>.

La lista de usuarios comienza vacía. Puede crear datos desde el shell de Django:

```powershell
python manage.py shell
```

```python
from apps.users.infrastructure.models import User

User.objects.create_user(
    username="ada",
    email="ada@example.edu",
    password="local-only-password",
    full_name="Ada Lovelace",
    role="professor",
)
```

## Stack completo en Docker

También puede ejecutar PostgreSQL y Django dentro de Docker. Si no creó `.env` en el inicio rápido, hágalo antes de iniciar el stack:

```powershell
Copy-Item .env.example .env
# Reemplace DJANGO_SECRET_KEY y POSTGRES_PASSWORD antes de iniciar.
```

```powershell
docker compose up --build
```

En este modo, Compose reemplaza internamente `POSTGRES_HOST` por `db` y `POSTGRES_PORT` por `5432`. Ejecute los comandos de Django dentro del contenedor:

```powershell
docker compose exec api python manage.py migrate
docker compose exec api python manage.py shell
```

Consulte [docs/environment.md](docs/environment.md) para conocer las variables y [docs/docker.md](docs/docker.md) para administrar los contenedores.

## Arquitectura

Cada feature vive en `apps/` y separa responsabilidades:

```text
interfaces -> application -> domain
     |              ^
     v              |
infrastructure -----+
```

- `domain`: reglas y tipos de negocio sin dependencias de Django.
- `application`: casos de uso y puertos requeridos por la aplicación.
- `infrastructure`: modelos ORM y adaptadores concretos.
- `interfaces`: contratos HTTP, serializadores, vistas y rutas.

La composición de dependencias se realiza en la vista por ahora. Cuando crezca el proyecto puede moverse a una factoría o contenedor sin alterar el dominio.

## Estructura

```text
./
├── apps/
│   ├── health/
│   └── users/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── interfaces/
├── config/settings/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Documentación

- [Arquitectura](docs/architecture.md)
- [Construcción del proyecto](docs/construccion.md)
- [Variables de entorno](docs/environment.md)
- [Endpoints](docs/endpoints.md)
- [Docker](docs/docker.md)
- [Reglas de colaboración](AGENTS.md)

## Calidad y SonarQube

Instale las herramientas de desarrollo:

```powershell
python -m pip install -r requirements-dev.txt
```

Antes de finalizar un cambio, ejecute las validaciones del proyecto:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate --file schema.yml
python -m pytest
python -m ruff check .
python -m ruff format --check .
docker compose config --quiet
```

`pytest` genera `coverage.xml`. `sonar-project.properties` configura Python 3.13, fuentes, pruebas, cobertura y exclusiones técnicas como migraciones.

## Decisiones de seguridad

Los endpoints públicos declaran `AllowAny` y desactivan autenticadores de forma explícita. El valor global exige autenticación para futuros endpoints, reduciendo el riesgo de publicar nuevas rutas por accidente. El serializador público enumera los únicos campos permitidos y el repositorio excluye usuarios inactivos o no públicos.

## Despliegue en Amazon

La ruta recomendada para Amazon ECS, ECR o App Runner es construir el `Dockerfile`. Así producción utiliza Python 3.13.13 y las mismas versiones exactas de dependencias que el entorno validado, independientemente del runtime preinstalado en la instancia anfitriona.
