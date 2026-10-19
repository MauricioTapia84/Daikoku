# Checklist de evaluación de progreso del proyecto Daikoku

Este documento funciona como una guía de seguimiento para evaluar el avance del proyecto respecto a la arquitectura del agente, la robustez técnica y la alineación con los ejemplos del profesor. La intención es que se vaya marcando cada punto como completado a medida que se implementen las mejoras.

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

## 11) Notas para el equipo

Este checklist debe usarse como una referencia viva. Cada vez que se complete una mejora, se marca la casilla correspondiente. La idea es llevar un registro claro del progreso y evitar que queden mejoras importantes sin documentar.

El enfoque principal para la próxima etapa es mejorar la arquitectura del agente siguiendo la lógica del profesor, manteniendo la línea de negocio del proyecto: un asistente académico para responder preguntas sobre documentos y material de estudio.
