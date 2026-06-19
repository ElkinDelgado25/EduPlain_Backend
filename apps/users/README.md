# Feature Users

Contiene el directorio de usuarios académicos y el modelo de usuario propio del proyecto. Su primer caso de uso lista únicamente usuarios activos y marcados como públicos.

Capas:

- `domain`: entidad pública y roles del negocio.
- `application`: puerto de repositorio y caso de uso de consulta.
- `infrastructure`: modelo Django y repositorio ORM.
- `interfaces`: contrato y endpoint REST.

El archivo raíz `models.py` es únicamente un puente para el autodiscovery de Django; la implementación persistente continúa en `infrastructure/models.py`.

No existen endpoints de login, JWT, creación, edición o eliminación. El modelo hereda de `AbstractUser` para habilitar una evolución posterior sin sustituir la tabla principal de identidad.
