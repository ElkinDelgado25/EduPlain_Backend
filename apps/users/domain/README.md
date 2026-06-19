# Capa Domain

Representa conceptos del negocio con Python puro. `PublicUser` es una entidad inmutable y `UserRole` define los roles conocidos actualmente.

Esta carpeta no puede importar Django, DRF, HTTP ni detalles de PostgreSQL. Así, las reglas del negocio se pueden probar sin levantar el framework.
