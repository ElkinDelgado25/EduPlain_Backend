# API, conexiones y credenciales

Esta guía resume cómo conectarse a la API de Eduplain en desarrollo y cómo manejar credenciales sin exponer secretos en el repositorio.

## Base local

```text
http://localhost:8000
```

URLs principales:

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`
- Health check: `http://localhost:8000/api/health/`
- Django Admin: `http://localhost:8000/admin/`

## Autenticación actual

Mientras no exista Microsoft OAuth, JWT o login propio, los endpoints protegidos usan **autenticación básica HTTP**.

En Swagger UI:

1. Abra `http://localhost:8000/api/docs/`.
2. Presione `Authorize`.
3. Use el `username` de Django y la contraseña configurada en el entorno local.

Credenciales locales esperadas para el superusuario bootstrap:

```text
username: valor de EDUPLAIN_BOOTSTRAP_ADMIN_USERNAME
password: valor de EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD
```

En este proyecto, los valores reales deben estar en `.env` o `.env.local`, nunca en archivos versionados.

## Variables de credenciales

El superusuario inicial se configura con:

```env
EDUPLAIN_BOOTSTRAP_ADMIN_USERNAME=
EDUPLAIN_BOOTSTRAP_ADMIN_EMAIL=
EDUPLAIN_BOOTSTRAP_ADMIN_FULL_NAME=
EDUPLAIN_BOOTSTRAP_ADMIN_ROLE=
EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD=
```

Reglas:

- Si `EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD` está vacío, el bootstrap se omite cuando se usa `--skip-if-unconfigured`.
- Si `EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD` tiene valor, las otras variables `EDUPLAIN_BOOTSTRAP_ADMIN_*` son obligatorias.
- El valor real de `EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD` no debe aparecer en Markdown, commits, logs públicos ni capturas.
- `.env` y `.env.local` están ignorados por Git.

## Conexión desde cliente HTTP

Ejemplo con PowerShell usando variables locales:

```powershell
$username = $env:EDUPLAIN_BOOTSTRAP_ADMIN_USERNAME
$password = $env:EDUPLAIN_BOOTSTRAP_ADMIN_PASSWORD
$pair = "${username}:${password}"
$token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))

Invoke-RestMethod `
  -Uri "http://localhost:8000/api/documents/pdfs/" `
  -Headers @{ Authorization = "Basic $token" }
```

Ejemplo conceptual para subir un PDF:

```powershell
$form = @{ file = Get-Item ".\silabo.pdf" }

Invoke-RestMethod `
  -Uri "http://localhost:8000/api/documents/pdfs/" `
  -Method Post `
  -Headers @{ Authorization = "Basic $token" } `
  -Form $form
```

## Endpoints públicos

Estos endpoints no requieren autenticación:

```text
GET /api/health/
GET /api/users/public/
```

## Endpoints protegidos actuales

Estos endpoints requieren autenticación básica:

```text
POST /api/documents/pdf-to-markdown/
POST /api/documents/pdfs/
GET /api/documents/pdfs/
GET /api/documents/pdfs/{id}/
```

## Conexiones de infraestructura

PostgreSQL local desde el host:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=55432
```

PostgreSQL dentro de Docker Compose:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Storage documental local:

```env
DOCUMENT_STORAGE_BACKEND=local
DOCUMENT_STORAGE_ROOT=media/documents
```

Conexión futura para backend NoSQL o storage externo:

```env
NOSQL_DATABASE_CONNECTION=
```

`NOSQL_DATABASE_CONNECTION` queda reservada para una integración posterior con MongoDB, S3 compatible, OneDrive u otro backend. No debe contener secretos reales en documentación versionada.

## Producción

En producción no se deben usar credenciales en archivos Markdown ni en `.env` versionados. Use el gestor de secretos de la plataforma, por ejemplo AWS Secrets Manager, SSM Parameter Store, variables seguras del proveedor de despliegue o equivalente.
