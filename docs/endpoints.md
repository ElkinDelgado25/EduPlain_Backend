# Endpoints

Base local: `http://localhost:8000`

Para detalles de autenticación, credenciales locales y ejemplos de conexión, consulte [`docs/api.md`](api.md).

Los endpoints protegidos usan autenticación básica HTTP mientras no exista login institucional o JWT. En Swagger UI, use `Authorize` con el `username` y la contraseña de un usuario activo, por ejemplo el superusuario bootstrap local. Los endpoints declarados como públicos no requieren autenticación.

## Estado del servicio

`GET /api/health/`

- Autenticación: no requerida.
- Objetivo: comprobar liveness del proceso y mostrar el entorno configurado.

Respuesta `200 OK`:

```json
{
  "status": "ok",
  "service": "eduplain-backend",
  "environment": "development"
}
```

## Usuarios públicos

`GET /api/users/public/`

- Autenticación: no requerida.
- Filtros internos: solo usuarios activos y con `is_public=true`.
- Orden: nombre completo y luego identificador.

Respuesta `200 OK`:

```json
[
  {
    "id": 1,
    "full_name": "Ada Lovelace",
    "email": "ada@example.edu",
    "role": "professor"
  }
]
```

Una instalación nueva devuelve `[]` hasta crear usuarios. Los únicos roles válidos actualmente son `student`, `professor` y `administrator`.

## Documentos

`POST /api/documents/pdf-to-markdown/`

- Autenticación: requerida por la política global del backend.
- Objetivo: convertir un PDF académico en Markdown para validar el procesamiento inicial de sílabos.
- Formato de envío: `multipart/form-data`.
- Campo requerido: `file`, con un PDF de hasta 10 MB.

Respuesta `200 OK`:

```json
{
  "filename": "silabo.pdf",
  "characters": 18420,
  "markdown": "# Contenido extraído..."
}
```

Errores esperados:

- `400 Bad Request` si el archivo no es PDF, supera el tamaño permitido o no puede convertirse.
- `401 Unauthorized` o `403 Forbidden` si la solicitud no está autenticada.

`POST /api/documents/pdfs/`

- Autenticación: requerida por la política global del backend.
- Objetivo: guardar un PDF académico en el storage documental configurado y devolver su metadata.
- Formato de envío: `multipart/form-data`.
- Campo requerido: `file`, con un PDF de hasta 10 MB.

Respuesta `201 Created`:

```json
{
  "id": "0b9d3f7a4f2d4fb58d8eec6a0a88b2b5",
  "filename": "silabo.pdf",
  "content_type": "application/pdf",
  "size_bytes": 18420,
  "storage_backend": "local",
  "storage_key": "pdfs/0b9d3f7a4f2d4fb58d8eec6a0a88b2b5-silabo.pdf",
  "created_at": "2026-06-23T12:00:00Z"
}
```

`GET /api/documents/pdfs/`

- Autenticación: requerida.
- Objetivo: consultar la metadata de PDFs guardados.

Respuesta `200 OK`:

```json
[
  {
    "id": "0b9d3f7a4f2d4fb58d8eec6a0a88b2b5",
    "filename": "silabo.pdf",
    "content_type": "application/pdf",
    "size_bytes": 18420,
    "storage_backend": "local",
    "storage_key": "pdfs/0b9d3f7a4f2d4fb58d8eec6a0a88b2b5-silabo.pdf",
    "created_at": "2026-06-23T12:00:00Z"
  }
]
```

`GET /api/documents/pdfs/{id}/`

- Autenticación: requerida.
- Objetivo: consultar la metadata de un PDF guardado por identificador.

Errores esperados:

- `400 Bad Request` si el archivo enviado no es PDF o supera el tamaño permitido.
- `404 Not Found` si el identificador no existe.
- `500 Internal Server Error` si el backend de storage no está disponible o no está implementado.

## OpenAPI

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/schema/` | Documento OpenAPI en formato descargable. |
| `GET` | `/api/docs/` | Interfaz Swagger UI. |

No existen rutas de login, emisión de tokens ni CRUD de usuarios en esta versión.
