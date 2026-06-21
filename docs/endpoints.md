# Endpoints

Base local: `http://localhost:8000`

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

## OpenAPI

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/schema/` | Documento OpenAPI en formato descargable. |
| `GET` | `/api/docs/` | Interfaz Swagger UI. |

No existen rutas de login, emisión de tokens ni CRUD de usuarios en esta versión.
