# Aspire

Aspire se usa como orquestador local alternativo a Docker Compose. No contiene lógica de negocio: solo inicia infraestructura y procesos de desarrollo para el backend Django.

## Versiones fijadas

| Componente | Versión |
|---|---:|
| .NET SDK | `10.0.201` |
| Aspire CLI | `13.4.6` |
| Aspire AppHost SDK | `13.4.6` |
| `Aspire.Hosting.PostgreSQL` | `13.4.6` |
| PostgreSQL container | `postgres:17-alpine` |

`global.json` fija el SDK de .NET con `rollForward=disable`. Si la versión no está instalada, instale `10.0.201` antes de ejecutar el AppHost.

## Recursos orquestados

- `postgres`: contenedor PostgreSQL con volumen `eduplain-aspire-postgres-data`.
- `academic-db`: base de datos creada desde `POSTGRES_DB`.
- `django-migrate`: ejecuta `python manage.py migrate --noinput`.
- `django-bootstrap`: ejecuta `python manage.py bootstrap_superuser --skip-if-unconfigured`.
- `django-api`: ejecuta `python manage.py runserver` y expone `/api/health/` como health check.

Aspire reutiliza `.venv` si existe. Si no encuentra `.venv`, resuelve `python` desde el `PATH`; ese intérprete debe cumplir el guard del proyecto: CPython `3.13.13` o parche posterior de la rama `3.13`.

## Configuración

El AppHost lee `.env` y luego `.env.local`, con la misma precedencia operativa que Django:

```text
variables del proceso > .env.local > .env
```

Antes de iniciar, configure como mínimo `DJANGO_SECRET_KEY` y `POSTGRES_PASSWORD` en `.env` o como variables del proceso. Las variables `EDUPLAIN_BOOTSTRAP_ADMIN_*` siguen siendo opcionales; si la contraseña bootstrap está vacía, el bootstrap se omite.

Por defecto Aspire usa puertos distintos para PostgreSQL y el mismo puerto para Django:

| Variable | Default | Uso |
|---|---:|---|
| `ASPIRE_DJANGO_PORT` | `8000` | Puerto del `runserver` de Django. |
| `ASPIRE_POSTGRES_PORT` | `55433` | Puerto local publicado por PostgreSQL de Aspire. |

`ASPIRE_POSTGRES_PORT=55433` evita colisionar con Docker Compose, que publica PostgreSQL en `55432`. Si también tiene el servicio `api` de Compose levantado, deténgalo o cambie `ASPIRE_DJANGO_PORT`.

## Ejecución

Desde la raíz del repositorio:

```powershell
dotnet build .\aspire\Eduplain.AppHost\Eduplain.AppHost.csproj
aspire run --apphost .\aspire\Eduplain.AppHost
```

También puede ejecutar desde la carpeta del AppHost:

```powershell
Set-Location .\aspire\Eduplain.AppHost
aspire run
```

Cuando el dashboard indique que `django-api` está saludable, use los endpoints habituales:

| Recurso | URL |
|---|---|
| Health check | <http://localhost:8000/api/health/> |
| Swagger UI | <http://localhost:8000/api/docs/> |
| Esquema OpenAPI | <http://localhost:8000/api/schema/> |

## Relación con Docker Compose

Docker Compose sigue siendo el flujo documentado para probar el stack contenedorizado completo. Aspire sirve para desarrollo local con observabilidad y orquestación de dependencias, manteniendo Django como proceso local.

Use una sola orquestación para la misma dependencia en un puerto determinado. Si Compose ya usa `8000` o `55432`, detenga esos servicios o ajuste los puertos `ASPIRE_*`.
