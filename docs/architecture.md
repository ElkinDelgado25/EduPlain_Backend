# Arquitectura

## Enfoque

El proyecto aplica DDD y Clean Architecture de forma pragmática. El objetivo inicial no es introducir abstracciones por volumen, sino mantener las decisiones de negocio separadas de Django, DRF y PostgreSQL.

La unidad principal de organización es la feature. Esto mantiene juntos los archivos que cambian por la misma razón y evita carpetas globales enormes de modelos, vistas o serializadores.

## Capas y dependencias

```text
HTTP request
    |
    v
interfaces -----> application -----> domain
    |                  ^
    v                  |
infrastructure --------+
    |
    v
PostgreSQL
```

### Domain

Contiene entidades, value objects, enumeraciones y reglas centrales. No conoce Django ni mecanismos de entrega o persistencia.

### Application

Define casos de uso y puertos. Coordina el dominio, pero no decide cómo se consulta PostgreSQL ni cómo se representa una respuesta HTTP.

### Infrastructure

Implementa detalles externos: modelos Django, repositorios ORM y, en el futuro, correo, almacenamiento o clientes de terceros.

### Interfaces

Traduce protocolos externos a operaciones de aplicación. En este proyecto contiene vistas, serializadores y URLs de DRF.

## Flujo de `GET /api/users/public/`

1. Django resuelve la URL hacia `PublicUserListView`.
2. La vista construye el repositorio concreto y el caso de uso.
3. `ListPublicUsers` pide información a su puerto de repositorio.
4. `DjangoPublicUserRepository` filtra el ORM y mapea filas a `PublicUser`.
5. `PublicUserSerializer` limita la respuesta al contrato público.

## Decisiones actuales

- Se usa un modelo de usuario propio desde la migración inicial para facilitar autenticación futura.
- El runtime se limita a CPython 3.13.13 o un parche posterior dentro de 3.13; Docker fija exactamente 3.13.13 para builds reproducibles.
- El email es público porque forma parte del contrato solicitado. `is_public` permite excluir usuarios del directorio.
- Los permisos globales de DRF son restrictivos. Solo health y el directorio declaran `AllowAny`.
- La inyección de dependencias se realiza manualmente en la vista; todavía no se justifica un contenedor.
- Health es un chequeo de liveness. No verifica PostgreSQL para no mezclar disponibilidad del proceso con readiness.
- `apps/users/models.py` es un puente de registro exigido por el autodiscovery de Django; no contiene lógica ni define otro modelo.

## Evolución prevista

Al incorporar autenticación, conviene crear casos de uso específicos y adaptadores separados para tokens. Los permisos por rol deben vivir como políticas explícitas y no como condiciones dispersas en las vistas. Las features académicas futuras —por ejemplo cursos, matrículas y calificaciones— deben conservar los mismos límites.
