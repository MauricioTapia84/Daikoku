# Prompt final para presentación del video de Daikoku

Eres un experto en presentaciones técnicas y storytelling para proyectos de IA. Tu tarea es preparar un material profesional para presentar Daikoku a una audiencia mixta: profesores, evaluadores y compañeros con distinto nivel técnico.

## Contexto del proyecto

Proyecto: Daikoku
Tipo: asistente académico para consulta documental
Enfoque principal: RAG + LangGraph + embeddings + memoria por sesión + recuperación externa
Objetivo: ayudar a usuarios a consultar material académico de forma inteligente, contextualizada y con evidencia documental.

## Idea central

Daikoku no es un simple chatbot: es un agente académico orientado a documentos. Responde preguntas usando evidencia recuperada del corpus del usuario y, cuando es necesario, complementa con información externa. El sistema combina recuperación semántica, orquestación por grafo, memoria por sesión y trazabilidad de cada paso.

## Público objetivo

- profesores
- evaluadores académicos
- compañeros con distinto nivel técnico
- personas interesadas en IA aplicada a documentos y estudio

## Estilo de presentación

- profesional
- claro y didáctico
- riguroso pero accesible
- orientado a demostrar valor real y arquitectura técnica sólida

## Duración sugerida

3 a 5 minutos, con una narrativa ordenada y visual limpia.

## Estructura recomendada del video

### 1. Introducción (15-20 segundos)
Plantear el problema de manejar demasiados documentos y mucha información dispersa. Mostrar la necesidad de un asistente que comprenda el contexto y responda con evidencia.

### 2. Problema y necesidad (20-30 segundos)
Explicar la diferencia entre responder sin evidencia y responder con contexto real. Presentar el caso de uso académico en documentos universitarios.

### 3. Solución propuesta (30-45 segundos)
Explicar que Daikoku es un agente que recupera contexto relevante, decide si necesita apoyo externo y responde con base documental.

### 4. Arquitectura técnica (45-60 segundos)
Mostrar los nodos principales: router, tool layer, retrieval, memory, observability y finalizer. Explicar cómo decide usar contexto local o externo.

### 5. Componentes clave (30-45 segundos)
- embeddings
- vector store
- memoria por sesión
- recuperación externa
- observabilidad del flujo

### 6. Validación y robustez (30-45 segundos)
Explicar que el sistema maneja preguntas vacías, ambiguas, historial persistente y trazas por ejecución. Mencionar pruebas y benchmark de recuperación.

### 7. Valor del proyecto (20-30 segundos)
Resaltar ahorro de tiempo, mayor precisión documental, continuidad de conversación y mejor comprensión del material.

### 8. Cierre (20-30 segundos)
Hacer un resumen final del proyecto y enfatizar que es una base sólida, extensible y técnica.

## Estructura sugerida de diapositivas

### Diapositiva 1: Título
- Daikoku
- Asistente académico para consulta de documentos

### Diapositiva 2: Problema
- documentación dispersa
- dificultad para localizar información relevante
- necesidad de apoyo para estudiar y consultar material académico

### Diapositiva 3: Solución
- recuperación semántica
- respuesta con evidencia documental
- memoria y contexto externo

### Diapositiva 4: Arquitectura
- diagrama del flujo del agente
- router, retrieval, memory, finalizer

### Diapositiva 5: Tool layer y flujo de decisiones
- buscar_documentos
- buscar_en_wikipedia
- resolver_ambigüedad
- resumir_historial

### Diapositiva 6: Recuperación semántica y vector store
- embeddings
- similitud
- FAISS / fallback

### Diapositiva 7: Memoria y observabilidad
- sesión persistente
- resumen del historial
- trazas y métricas para auditoría

### Diapositiva 8: Validación y resultados
- pruebas del agente
- benchmark de recuperación
- robustez del sistema

### Diapositiva 9: Valor y cierre
- utilidad académica
- potencial de extensión
- conclusión del proyecto

## Guion de voz en off sugerido

"Daikoku es un asistente académico para consultar documentos de manera inteligente. En lugar de responder solo con conocimiento general, el sistema recupera evidencia del corpus del usuario, decide si necesita contexto externo y genera respuestas con base documental. La arquitectura combina un flujo con LangGraph, recuperación semántica, memoria por sesión y observabilidad del proceso. Esto permite que el sistema no solo responda, sino que lo haga de forma trazable, contextualizada y útil para estudiantes, docentes y evaluadores."

## Reglas importantes

- usar lenguaje claro y técnico, pero explicando cada concepto
- no abusar de jerga sin contexto
- enfatizar la diferencia entre contexto local y contexto externo
- hablar de validación, trazabilidad y utilidad académica
- dejar la presentación sólida, moderna y alineada con un proyecto de IA con rigor técnico

## Prompt final para IA generadora

Genera una presentación técnica y didáctica del proyecto Daikoku, con enfoque académico y de evaluación. Explica el problema, la solución propuesta, la arquitectura del sistema, la capa de herramientas, el router, la recuperación local y externa, el vector store, la memoria, la observabilidad y la validación. El público es mixto: profesores, evaluadores y compañeros con distinto nivel técnico. Usa lenguaje claro, profesional y didáctico. Incluye: guion de voz en off, estructura de diapositivas, mensajes visuales, tiempos estimados por sección y tono de presentación. Haz que la presentación se vea robusta, moderna y alineada con un proyecto de IA con base académica y rigor técnico.
