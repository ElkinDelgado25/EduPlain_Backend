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

## OpenAPI

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/schema/` | Documento OpenAPI en formato descargable. |
| `GET` | `/api/docs/` | Interfaz Swagger UI. |

No existen rutas de login, emisión de tokens ni CRUD de usuarios en esta versión.
