# Feature Health

Expone `GET /api/health/` para comprobar que el proceso HTTP está disponible y conocer el entorno activo.

Esta comprobación es intencionalmente ligera: no consulta la base de datos ni servicios externos. Más adelante puede añadirse un endpoint de readiness separado si la infraestructura necesita verificar dependencias.

La feature solo tiene capa `interfaces` porque no contiene reglas de negocio ni persistencia.
