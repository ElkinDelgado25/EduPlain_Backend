# Capa Infrastructure

Contiene detalles reemplazables del framework y la persistencia:

- `models.py`: representación ORM y esquema persistente.
- `repositories.py`: adaptador que consulta Django y devuelve entidades del dominio.
- `migrations/`: historial versionado del esquema.

Los modelos de Django no deben llegar a la capa de aplicación ni usarse como respuesta directa de una API.
