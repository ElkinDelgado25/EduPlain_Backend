# Construcción del proyecto

Este documento describe la dirección de construcción de Eduplain. No todo lo descrito aquí está implementado todavía; funciona como guía para ordenar el producto, la arquitectura y las fases técnicas.

## Concepto central

Eduplain se orienta a ser un **sistema de transformación de sílabos en rutas de aprendizaje**.

La plataforma convierte el sílabo de una asignatura, normalmente usado como documento formal de planificación, en una ruta de aprendizaje interactiva que ayuda a estudiantes y docentes a comprender qué estudiar, en qué orden avanzar y cómo conectar los contenidos con acciones concretas de aprendizaje.

## Objetivo general

Desarrollar un sistema web que transforme sílabos universitarios en rutas de aprendizaje estructuradas mediante inteligencia artificial, con el fin de apoyar a estudiantes y docentes en la organización, comprensión y continuidad del aprendizaje en asignaturas de alta complejidad.

## Problema que resuelve

Aunque el acceso al conocimiento está más democratizado por internet, plataformas educativas e inteligencia artificial, muchos estudiantes siguen teniendo dificultades para saber qué estudiar, en qué orden avanzar, cómo organizarse y cómo conectar los contenidos de una asignatura con acciones concretas de aprendizaje.

Desde la perspectiva estudiantil, el sílabo suele percibirse como un documento largo, formal y poco práctico, por lo que muchas veces no se usa como ruta activa de estudio.

Desde la perspectiva docente, el sílabo contiene la planificación oficial de la materia, pero transformarlo en materiales claros, actividades, preguntas o guías requiere tiempo, organización y esfuerzo.

## Qué es y qué no es

Eduplain no debe construirse como un chatbot general. La base del producto es una plataforma de rutas académicas basadas en sílabos.

Sí es:

- Un puente entre el sílabo oficial y el estudio práctico.
- Una herramienta de apoyo para estudiantes y docentes.
- Una guía estructurada para materias universitarias complejas.
- Una base para usar IA de forma dirigida, contextualizada y revisable.

No es:

- Un reemplazo del docente.
- Un lector de PDF sin estructura.
- Un generador de resúmenes aislado.
- Un chatbot sin contexto académico.

## Arquitectura general

El frontend y el backend se mantienen como proyectos separados.

```text
eduplain-frontend
  -> experiencia visual del usuario
  -> subida de sílabos y documentos
  -> visualización de rutas, unidades, temas y extras
  -> consumo de la API del backend

eduplain-backend
  -> Django REST Framework
  -> reglas de negocio y persistencia
  -> procesamiento de PDF
  -> orquestación con LangGraph
  -> integración con LangChain y modelos de IA
  -> almacenamiento en PostgreSQL y pgvector
```

La regla principal es:

```text
Frontend = experiencia de usuario
Backend = lógica, seguridad, datos, IA y orquestación
```

Las API keys de proveedores de IA, Microsoft o servicios externos nunca deben vivir en el frontend.

## Flujo principal del producto

```text
Docente o administrador sube el sílabo en PDF
  -> el backend guarda el archivo
  -> el backend convierte el PDF a Markdown o texto limpio
  -> LangGraph orquesta el análisis del sílabo
  -> la IA identifica datos generales, unidades, temas y subtemas
  -> el sistema genera una ruta de aprendizaje estructurada
  -> el backend valida y guarda la estructura
  -> el frontend muestra la ruta de forma editable y navegable
```

## Entrada y salida esperada

Entrada inicial:

- PDF del sílabo.
- Datos de la materia si el usuario los proporciona.
- Instrucciones del docente.
- Documentos adicionales para RAG, si existen.
- Extras manuales agregados desde la web.

Salida estructurada:

- Materia.
- Objetivo general.
- Unidades del sílabo, normalmente cuatro.
- Temas por unidad.
- Subtemas o temas hijos.
- Explicaciones generadas o manuales.
- Actividades sugeridas.
- Preguntas de práctica.
- Recursos o documentos relacionados.
- Relaciones entre temas.

Ejemplo conceptual:

```text
Cálculo Diferencial

Unidad 1: Funciones y límites
Tema: Funciones
Subtemas:
- Dominio
- Rango
- Gráficas
- Funciones por partes

Extra docente:
Antes de estudiar límites, repasar dominio y rango.

Acciones sugeridas:
- Leer explicación breve
- Resolver ejercicios básicos
- Revisar relación con límites
```

## Orquestación con LangGraph

LangGraph debe coordinar los pasos del agente. No reemplaza al modelo de IA; organiza cuándo usar código normal, herramientas, modelos y validaciones.

Flujo inicial recomendado:

```text
START
  -> recibir_pdf
  -> convertir_pdf_a_markdown
  -> extraer_datos_generales
  -> detectar_unidades
  -> extraer_temas_por_unidad
  -> generar_temas_hijos
  -> generar_acciones_de_aprendizaje
  -> validar_resultado
  -> guardar_estructura
END
```

Responsabilidades por tipo de paso:

- Conversión de PDF: código Python y librerías de extracción.
- Extracción y organización: modelo de IA mediante LangChain.
- Validación: código Python, esquemas y reglas de negocio.
- Persistencia: repositorios del backend.
- Respuesta al usuario: API Django y frontend.

## Uso de LangChain y modelos de IA

LangChain debe usarse como capa de integración con modelos, prompts, structured outputs, retrievers y tools.

OpenAI u otro proveedor de IA recibe texto ya extraído, instrucciones y un formato de salida esperado. No conviene mandar el PDF crudo como única entrada para todo el flujo.

Formato recomendado:

```text
PDF
  -> Markdown/texto limpio
  -> prompt con instrucciones
  -> salida JSON estructurada
  -> validación backend
  -> almacenamiento en base de datos
```

La salida del modelo debe ser estructurada, preferiblemente JSON validable, para evitar que el frontend dependa de texto libre.

## Conversión de PDF a Markdown

Para sílabos con texto real, se puede usar una librería de conversión de PDF a Markdown o texto, por ejemplo `pymupdf4llm`.

El primer bloque backend implementado expone `POST /api/documents/pdf-to-markdown/`, que recibe un PDF autenticado por `multipart/form-data`, lo convierte a Markdown y devuelve el nombre del archivo, la cantidad de caracteres extraídos y el Markdown resultante. Este endpoint sirve como laboratorio técnico antes de construir la interfaz frontend.

También se deja una base inicial de almacenamiento documental con `POST /api/documents/pdfs/`, `GET /api/documents/pdfs/` y `GET /api/documents/pdfs/{id}/`. El adaptador actual guarda PDFs en filesystem local y catálogo JSON. La variable `NOSQL_DATABASE_CONNECTION` queda reservada para sustituir ese adaptador por un backend MongoDB, S3 compatible, OneDrive u otro storage externo.

Para PDFs escaneados o basados en imágenes, se necesitará OCR antes de generar Markdown.

Flujo recomendado:

```text
PDF con texto real
  -> extracción directa
  -> Markdown
  -> chunks
  -> embeddings
  -> pgvector

PDF escaneado
  -> OCR
  -> texto
  -> Markdown
  -> chunks
  -> embeddings
  -> pgvector
```

## Módulos backend propuestos

La implementación debe respetar la arquitectura actual del repositorio, separando dominio, aplicación, infraestructura e interfaces.

```text
apps/
  syllabi/
    domain/
    application/
    infrastructure/
    interfaces/

  learning_paths/
    domain/
    application/
    infrastructure/
    interfaces/

  ai_agents/
    domain/
    application/
    infrastructure/
      langgraph/
      langchain/
    interfaces/

  documents/
    domain/
    application/
    infrastructure/
    interfaces/
```

`domain/` no debe depender de Django, DRF, bases de datos, LangChain, LangGraph ni clientes externos.

`application/` debe definir casos de uso y puertos.

`infrastructure/` debe implementar ORM, servicios externos, PDF, OneDrive, vector store y proveedores de IA.

`interfaces/` debe contener vistas, serializadores y rutas HTTP.

## Modelo conceptual de datos

Modelo base sugerido:

```text
AcademicPeriod
  - year
  - term
  - label

Course
  - name
  - code
  - period_id

Syllabus
  - course_id
  - original_pdf
  - markdown_content
  - processing_status

LearningPath
  - course_id
  - title
  - status

LearningUnit
  - learning_path_id
  - number
  - title
  - summary

Topic
  - unit_id
  - parent_topic_id
  - title
  - description
  - source

TopicExtra
  - topic_id
  - title
  - content
  - created_by
  - is_manual

DocumentSource
  - course_id
  - source_type
  - file_name
  - processing_status
  - external_file_id
```

`parent_topic_id` permite representar temas hijos o relaciones jerárquicas.

`TopicExtra` permite agregar explicaciones o materiales manuales sin sobrescribir lo generado por IA.

## Frontend separado

El frontend debe vivir en otro repositorio, por ejemplo:

```text
eduplain-frontend/
eduplain-backend/
```

Responsabilidades del frontend:

- Pantalla de inicio y autenticación.
- Subida de sílabos y documentos.
- Visualización de ruta por periodo, materia y unidad.
- Árbol de unidades, temas y subtemas.
- Edición de extras manuales.
- Estados de procesamiento.
- Manejo de errores y límites de uso.
- Consumo de endpoints del backend.

Responsabilidades que no deben estar en el frontend:

- API keys.
- Lógica de LangGraph.
- Llamadas directas a OpenAI u otros LLM.
- Validación de seguridad como única barrera.
- Persistencia principal.

## Microsoft OAuth y OneDrive

Microsoft OAuth encaja con el enfoque institucional del proyecto.

Fase inicial recomendada:

```text
Login institucional con Microsoft
  -> validar identidad
  -> crear o actualizar usuario local
  -> asignar rol estudiante, docente o administrador
```

Scopes iniciales para login:

```text
openid
profile
email
User.Read
```

La integración con OneDrive debe ser una fase posterior. Puede servir para crear carpetas por periodo y materia, exportar rutas y guardar PDFs de apoyo.

Estructura sugerida en OneDrive:

```text
OneDrive/
  Eduplain/
    2026-01/
      Calculo Diferencial/
        00_silabo/
          silabo.pdf

        01_rutas_de_aprendizaje/
          unidad_1_funciones_y_limites.pdf
          unidad_2_derivadas.pdf
          unidad_3_aplicaciones.pdf
          unidad_4_integrales.pdf

        02_fuentes_rag/
          documento_1.pdf
          documento_2.pdf
          documento_3.pdf
          documento_4.pdf
          documento_5.pdf

        03_extras_docente/
          explicaciones_manual.md

        metadata.json
```

Scopes adicionales para OneDrive, si se implementa:

```text
Files.ReadWrite
```

OneDrive no debe reemplazar la base de datos. OneDrive sirve para archivos y exportaciones; PostgreSQL conserva la estructura, permisos, estados y metadatos.

## RAG con documentos adicionales

La función de RAG debe permitir asociar documentos extra a una materia o ruta de aprendizaje.

Flujo recomendado:

```text
Usuario agrega hasta 5 PDFs de apoyo
  -> backend guarda o importa documentos
  -> convierte PDF a Markdown
  -> divide contenido en chunks
  -> genera embeddings
  -> almacena vectores en pgvector
  -> el agente consulta ese contexto cuando responde o genera contenido
```

Los documentos RAG deben estar relacionados con una materia, periodo o ruta específica para evitar mezclar contextos.

## Rate limit y control de costos

El rate limit real debe aplicarse en el backend.

Primera capa:

- Throttling de Django REST Framework por usuario, IP y endpoint.
- Límite específico para endpoints de IA.

Segunda capa:

- Redis como backend de cache en producción.
- Cuotas por usuario o rol.

Tercera capa:

- Registro de tokens usados.
- Límite diario de mensajes o generaciones.
- Límite de tamaño de PDF y cantidad de documentos.
- Control de costo por usuario, materia o institución.

Endpoint de IA sugerido:

```text
POST /api/ai/chat/
  -> validar usuario
  -> revisar rate limit
  -> revisar cuota diaria
  -> ejecutar LangGraph
  -> registrar tokens y costo
  -> responder
```

## Deployment stack esperado

Stack inicial recomendado:

```text
Frontend
  -> Vercel, Netlify o S3 + CloudFront

Backend
  -> Docker
  -> AWS App Runner o ECS Fargate

Base de datos
  -> Amazon RDS PostgreSQL

Vector search
  -> pgvector sobre PostgreSQL

Secretos
  -> AWS Secrets Manager o SSM Parameter Store

Logs
  -> CloudWatch

Observabilidad IA
  -> LangSmith
```

Para la primera versión, App Runner puede ser más simple que ECS. ECS Fargate tiene más control, pero también más configuración.

## Endpoints futuros sugeridos

Estos endpoints son una guía conceptual, no una lista implementada.

```text
POST /api/syllabi/upload/
POST /api/syllabi/{id}/process/
GET /api/syllabi/{id}/

GET /api/learning-paths/{id}/
POST /api/learning-paths/{id}/approve/

POST /api/topics/{id}/extras/
POST /api/topics/{id}/generate-children/

POST /api/documents/rag/upload/
POST /api/documents/{id}/process/

GET /api/auth/microsoft/login/
GET /api/auth/microsoft/callback/

POST /api/onedrive/folders/sync/
POST /api/learning-paths/{id}/export/
```

Cada endpoint nuevo debe documentarse en OpenAPI y en `docs/endpoints.md` cuando se implemente.

## MVP recomendado

Primera versión funcional:

- Subir PDF del sílabo desde la web.
- Convertir PDF a Markdown o texto limpio.
- Extraer materia, objetivo y unidades.
- Extraer temas por unidad.
- Mostrar ruta de aprendizaje en frontend.
- Permitir agregar explicaciones manuales a un tema.
- Permitir generar temas hijos con IA.
- Guardar estructura en PostgreSQL.

No incluir inicialmente:

- Integración completa con OneDrive.
- Chat general avanzado.
- Teams, calendario o correo.
- Automatizaciones institucionales complejas.
- CRUD completo de usuarios si el alcance todavía no lo requiere.

## Fases de construcción

Fase 1: Base del producto.

- Modelar sílabos, unidades, temas y extras.
- Crear subida de PDF.
- Convertir PDF a Markdown.
- Generar estructura inicial con IA.
- Visualizar y editar ruta.

Fase 2: Agente académico.

- Crear grafo LangGraph para análisis de sílabos.
- Agregar generación de temas hijos.
- Agregar acciones de aprendizaje.
- Agregar validación estructurada de salida.

Fase 3: RAG.

- Subir documentos extra.
- Procesar chunks y embeddings.
- Guardar vectores en pgvector.
- Usar documentos como contexto para generación y consulta.

Fase 4: Identidad institucional.

- Implementar Microsoft OAuth.
- Mapear roles estudiante, docente y administrador.
- Aplicar permisos por materia y ruta.

Fase 5: OneDrive.

- Crear carpeta `Eduplain/{periodo}/{materia}`.
- Exportar rutas de aprendizaje.
- Importar PDFs desde OneDrive.
- Sincronizar metadatos de archivos.

Fase 6: Operación y escalamiento.

- Agregar rate limit con Redis.
- Registrar consumo de tokens.
- Agregar observabilidad con LangSmith.
- Desplegar frontend y backend separados.
- Configurar backups y monitoreo.

## Decisiones de seguridad

- Las credenciales y API keys se leen desde variables de entorno.
- El frontend nunca almacena secretos de OpenAI, Microsoft ni proveedores externos.
- Los endpoints públicos deben ser explícitos.
- Los endpoints nuevos heredan autenticación global salvo decisión documentada.
- Las salidas públicas deben usar serializadores explícitos.
- Los archivos subidos deben validarse por tamaño, tipo y permisos.
- La IA no debe ejecutar código arbitrario ni acceder a herramientas no controladas.

## Criterios de calidad

Antes de finalizar cambios del backend:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate --file schema.yml
python -m pytest
python -m ruff check .
python -m ruff format --check .
docker compose config --quiet
```

Además, cuando se implementen agentes IA:

- Validar salidas del modelo con esquemas.
- Guardar estados de procesamiento.
- Registrar errores recuperables.
- No depender de texto libre para persistencia crítica.
- Agregar pruebas a reglas de negocio y validaciones.
