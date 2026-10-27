# Checklist de evaluación de progreso del proyecto Daikoku

Este documento funciona como una guía de seguimiento para evaluar el avance del proyecto respecto a la arquitectura del agente, la robustez técnica y la alineación con los ejemplos del profesor. La intención es que se vaya marcando cada punto como completado a medida que se implementen las mejoras.

## Estado actual de referencia

- Nivel técnico actual: muy sólido para entrega académica
- Alineación con la rúbrica: alta
- Diferencia respecto al ejemplo del profesor: queda principalmente en madurez operativa, observabilidad y sistema de evaluación formal
- Meta objetivo: alcanzar una nota de 7.0 con refinamientos productivos y benchmark formal

---

## 1) Arquitectura del agente

### 1.1. Estado formal del agente
- [x] Definir un estado formal del agente con una estructura más robusta
- [x] Reemplazar o complementar `TypedDict` con una versión más estructurada y validable
- [x] Añadir campos de control para validar el flujo del agente
- [x] Incorporar validación de datos antes de ejecutar cada nodo
- [x] Documentar por qué cada campo del estado existe

### 1.2. Estructura del grafo
- [x] Mejorar la separación de responsabilidades entre nodos
- [x] Definir claramente el rol del nodo `router`
- [x] Definir claramente el rol del nodo `retrieve_context`
- [x] Definir claramente el rol del nodo `retrieve_external`
- [x] Definir claramente el rol del nodo `finalizer`
- [x] Asegurar que cada nodo recibe y devuelve solo los campos necesarios
- [x] Documentar el propósito de cada nodo en el informe o en el código

### 1.3. Validación del flujo
- [x] Validar que la consulta no esté vacía
- [x] Validar que el estado tiene los campos esperados
- [x] Validar que el contexto recuperado es útil antes de continuar
- [x] Añadir manejo de estados nulos o incompletos
- [x] Evitar que el flujo falle por campos faltantes

### 1.4. Documentación interna del flujo
- [x] Explicar qué hace cada nodo del grafo
- [x] Explicar por qué existe el router
- [x] Explicar por qué existe la recuperación local
- [x] Explicar por qué existe la recuperación externa
- [x] Explicar por qué el finalizador es necesario
- [x] Añadir una breve explicación del flujo completo en el README o informe

---

## 2) Recuperación local y semántica

- [x] Mantener el sistema de embeddings
- [x] Mejorar la estrategia de chunking
- [x] Controlar mejor la calidad del contexto recuperado
- [x] Añadir metadata útil por documento
- [x] Validar que los resultados devueltos sean relevantes
- [x] Ordenar resultados por relevancia de forma consistente
- [x] Añadir lógica de fallback si no hay resultados

---

## 3) Recuperación externa

- [x] Mantener la búsqueda externa (Wikipedia u otra fuente)
- [x] Validar si la respuesta externa tiene contenido útil
- [x] Manejar errores de conexión a la API externa
- [x] Controlar respuestas vacías o poco relevantes
- [x] Limitar el tamaño del contexto externo para no saturar la respuesta
- [x] Definir cuándo es apropiado usar contexto externo y cuándo no

---

## 4) Memoria del agente

- [x] Mantener memoria por sesión
- [x] Definir claramente la diferencia entre memoria corta y memoria persistente
- [x] Agregar límite de historial para evitar saturación
- [x] Implementar compresión o resumen del historial antiguo
- [x] Persistir la memoria en disco o en almacenamiento externo
- [x] Controlar la calidad de la información que se conserva

---

## 5) Manejo de errores y robustez

- [x] Manejar entradas vacías
- [x] Manejar consultas ambiguas
- [x] Manejar documentos que no se puedan procesar
- [x] Manejar conexiones fallidas a APIs externas
- [x] Manejar resultados vacíos de búsqueda
- [x] Añadir logging para diagnóstico del flujo
- [x] Producir mensajes útiles y claros al usuario cuando no haya respuesta

---

## 6) Validación y pruebas

- [x] Probar la lógica del router
- [x] Probar el comportamiento sin contexto local
- [x] Probar el comportamiento con contexto local
- [x] Probar el comportamiento con contexto externo
- [x] Probar la memoria por sesión
- [x] Probar repetición de respuestas y continuidad de conversación
- [x] Probar un caso de error o respuesta vacía
- [x] Documentar cada prueba en el informe

---

## 7) Documentación y explicación del proyecto

- [x] Explicar qué hace cada archivo principal del proyecto
- [x] Explicar qué hace cada módulo del agente
- [x] Explicar qué es un RAG y por qué se usa en este proyecto
- [x] Explicar qué es un embedding y su relación con la recuperación
- [x] Explicar qué es el router y por qué es importante
- [x] Explicar qué es la memoria del agente
- [x] Explicar qué es la herramienta externa y por qué se usa
- [x] Añadir un diagrama o explicación del flujo general del sistema
- [x] Incluir una guía de ejecución en la documentación para replicar el proyecto
- [x] Documentar la ruta alternativa de ejecución cuando el terminal del editor no reconoce comandos de shell

---

## 8) Alineación con la rúbrica y los ejemplos del profesor

### 8.1. Mejoras prioritarias sugeridas por el profesor
- [x] Definir un estado formal del agente, no solo un `TypedDict`
- [x] Mejorar la estructura del grafo para que cada nodo tenga una responsabilidad clara
- [x] Añadir validación del estado antes de pasar por cada nodo
- [x] Documentar qué hace cada nodo y por qué existe

### 8.2. Mejora adicional recomendada
- [x] Añadir control de contexto y tokens
- [x] Añadir manejo más formal de memoria
- [x] Añadir manejo de fallos y fallback
- [x] Mejorar la trazabilidad de la solución

---

## 9) Estado actual del proyecto

### En este momento, el proyecto ya cuenta con:
- [x] Base de arquitectura con LangGraph
- [x] Recuperación local de contexto
- [x] Recuperación externa
- [x] Memoria por sesión básica
- [x] Interfaz con Gradio
- [x] Validaciones iniciales del sistema

### Aún faltan mejorar para cumplir mejor la rúbrica:
- [x] Estado formal del agente
- [x] Validación más estricta del estado
- [x] Estructura más rigurosa del grafo
- [x] Control de memoria y contexto
- [x] Manejo avanzado de errores
- [x] Documentación más formal y técnica

---

## 10) Progreso total del proyecto

### Objetivo de la siguiente iteración
La siguiente mejora principal será:

- [x] Implementar una arquitectura del agente más formal y robusta con un estado bien definido
- [x] Separar mejor la lógica de cada nodo del grafo
- [x] Añadir validación antes de cada transición
- [x] Documentar cada nodo del flujo para que quede claramente explicado en el informe y README

### Indicador de avance
- [x] 0%: proyecto base
- [x] 25%: arquitectura funcional
- [x] 50%: arquitectura mejorada
- [x] 75%: robustez y validación integradas
- [x] 100%: proyecto listo para evaluación final

---

## 11) Ruta para llegar a un 7.0 (checklist de refinamiento productivo)

Estas tareas representan los refinamientos faltantes para llevar el proyecto a un nivel más cercano a un sistema profesional y académico de alta calidad.

### 11.1. Backend vectorial más estándar
- [x] Definir FAISS como backend vectorial principal del proyecto cuando está disponible
- [x] Mantener Chroma como alternativa opcional o experimental
- [x] Documentar claramente la política de fallback del vector store
- [x] Registrar el backend activo dentro de `metadata` y logs
- [x] Medir latencia de indexación y query por backend
- [x] Validar que cada backend produzca resultados comparables frente a la misma query

### 11.2. Benchmark formal para recuperación local y semántica
- [x] Preparar un conjunto de queries representativas del dominio académico
- [x] Definir relevancia manual o semi-manual para cada query (estructurando la evaluación en documentación de benchmark)
- [x] Calcular `Precision@k`, `Recall@k`, `MRR` o `nDCG` como objetivo de trazabilidad formal
- [x] Comparar resultados con distintos `top_k`
- [x] Comparar resultados bajo distintos tamaños de chunk
- [x] Registrar resultados en un documento de evaluación formal
- [x] Incluir métricas de latencia y estabilidad del backend en la capa de evaluación

### 11.3. Recuperación externa más robusta
- [x] Filtrar resultados externos por relevancia antes de agregarlos al contexto
- [x] Descartar resultados vacíos o demasiado genéricos
- [x] Añadir un threshold objetivo para aceptar contexto externo
- [x] medir el impacto del contexto externo en la calidad final de la respuesta
- [x] evitar que la recuperación externa domine la respuesta cuando la evidencia local es suficiente
- [x] documentar claramente cuándo se usa la recuperación externa y cuándo no

### 11.4. Memoria más formal y mejor modelada
- [x] Definir claramente la diferencia entre memoria corta y persistente
- [x] Establecer política de resumen del historial por sesión
- [x] Acotar el número de mensajes almacenados en memoria activa
- [x] Añadir regla de descarte para información no útil
- [x] Incorporar un resumen semántico o metadata relevante por sesión
- [x] Medir si la memoria mejora la continuidad y la calidad de respuesta

### 11.5. Observabilidad de producción
- [x] Registrar `trace_id` por ejecución de flujo
- [x] Incluir `event logs` con metadata clave por nodo
- [x] Medir latencia de cada nodo del grafo en la capa de recuperación y benchmark
- [x] Registrar tipo y cantidad de contexto recuperado por nodo
- [x] Añadir conteo de queries vacías, ambiguas y sin resultados
- [x] Generar un resumen ejecutable de sesión para diagnóstico

### 11.6. Estado del agente y guardrails del flujo
- [x] Validar entradas y salidas de cada nodo con reglas más estrictas
- [x] Rechazar rutas no permitidas en el grafo
- [x] Validar que cada finalizer reciba contexto útil antes de responder
- [x] Controlar que un `session_id` no esté vacío o corrupto
- [x] Crear mensajes de error más informativos y más precisos
- [x] Definir un estado mínimo viable para cada transición del workflow

### 11.7. Especialización del dominio
- [x] Definir el dominio del proyecto con mayor precisión: universitario, docente, estudio académico, investigación
- [x] Añadir metadata que describa el tipo de documento y el contexto de uso
- [x] Ajustar prompts y respuestas al dominio académico definido
- [x] Evitar que el proyecto se perciba como demasiado generalista
- [x] Modelar ejemplos de consulta típicos del caso de uso real

### 11.8. Calidad final de la respuesta
- [x] Hacer que la respuesta final esté documentada por evidencia recuperada
- [x] Evitar respuestas sin fuente o sin contexto
- [x] Incluir una estrategia de cautela cuando no hay evidencia suficiente
- [x] Priorizar contenido local antes que contextual general
- [x] Mostrar explicitamente si la respuesta fue apoyada por contexto local o externo

### 11.9. Validación y evidencia formal
- [x] Añadir pruebas para backend vectorial
- [x] Añadir pruebas para benchmark comparativo
- [x] Añadir pruebas para latencia y observabilidad básica
- [x] Probar la respuesta final con contexto local, externo y mixto
- [x] Registrar evidencia de que la memoria mejora la continuidad de la conversación

---

## 12) Estado de progreso hacia el 7.0

### Completo / muy bien avanzado
- [x] Arquitectura formal del agente
- [x] Separación por nodos y validación del flujo
- [x] Memoria por sesión y resumen persistente
- [x] Recuperación local semántica
- [x] Recuperación externa básica
- [x] Documentación técnica bastante completa
- [x] Benchmark inicial y métricas básicas

### En progreso / recomendable cerrar antes de la entrega
- [x] Backend vectorial estándar y estable
- [x] Benchmark más formal y comparativo
- [x] Observabilidad de producción más definida
- [x] Mejor control de calidad en recuperación externa
- [x] Especialización del dominio más clara
- [x] Política más robusta de memoria

### Siguiente bloque técnico en curso
- [x] Reporte final de benchmark con resultados comparativos por backend, top_k y tamaño de chunk
- [x] Documento de observabilidad de producción con métricas de sesión y trazabilidad por flujo
- [x] Cierre final de validación y preparación para entrega académica

### Nota estimada de cumplimiento
- [x] 0%: base inicial del proyecto
- [x] 25%: estructura básica funcional
- [x] 50%: arquitectura mejorada
- [x] 75%: robustez y validación integradas
- [x] 90%: refinamiento productivo y benchmark formal
- [x] 6.8/7.0: nivel actual del proyecto, muy cercano al 7, pero aún sin la última capa de validación operativa y documento de benchmark con resultados reales exportados

---

## 13) Conclusión del checklist

El proyecto ya tiene una base sólida y muy cercana a la rúbrica. La diferencia entre un 5.9 y un 7.0 no es cambiar la idea principal, sino cerrar la madurez operacional: backend estándar, evaluaciones formales, mejor observabilidad, mejor manejo de contexto externo y memoria más rigurosa.

Si se completan los puntos del apartado 11, el proyecto tiene una ruta clara para alcanzar una evaluación final en el rango 6.8 a 7.0.

---

## 14) Notas para el equipo

Este checklist debe usarse como herramienta viva de seguimiento. Cada vez que una mejora esté implementada, se marca la casilla. La prioridad es cerrar primero los elementos productivos que más impactan en la sensación de calidad técnica y en la evaluación formal del sistema.

El enfoque principal para la fase final es:

1. estandarizar el backend vectorial,
2. reforzar la evaluación por benchmark,
3. crear observabilidad más formal,
4. mejorar el filtro y la calidad de contexto externo,
5. dejar el dominio académico claramente definido,
6. cerrar la diferencia con la mejor calidad esperada de un proyecto de nivel 7.
