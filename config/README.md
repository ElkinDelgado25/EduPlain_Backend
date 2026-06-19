# Configuración Django

Esta carpeta contiene el punto de composición global del proyecto:

- `settings/`: ajustes comunes y variantes por entorno.
- `urls.py`: enrutamiento principal y documentación OpenAPI.
- `asgi.py` y `wsgi.py`: entradas para servidores de aplicación.

Las reglas de negocio no deben vivir aquí. Los ajustes comunes pertenecen a `base.py`; las diferencias operativas van en el archivo del entorno correspondiente.
