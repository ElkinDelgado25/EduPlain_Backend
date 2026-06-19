# Capa Application

Orquesta las acciones disponibles para los consumidores del sistema. `ListPublicUsers` expresa el caso de uso actual y depende del protocolo `PublicUserRepository`.

El protocolo es un puerto: define lo que la aplicación necesita sin decidir si los datos provienen de PostgreSQL, memoria u otro servicio. La infraestructura proporciona la implementación concreta.
