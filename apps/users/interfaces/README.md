# Capa Interfaces

Adapta HTTP y Django REST Framework a los casos de uso:

- `serializers.py` define el contrato público de salida.
- `views.py` compone dependencias, ejecuta el caso de uso y crea la respuesta.
- `urls.py` publica las rutas de la feature.

El endpoint actual usa `AllowAny` y una lista vacía de autenticadores de forma intencional. Cualquier campo público nuevo debe añadirse conscientemente al serializador y documentarse.
