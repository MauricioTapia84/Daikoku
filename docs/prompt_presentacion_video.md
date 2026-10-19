# Prompt para IA: presentación del proyecto Daikoku

Eres un experto en presentaciones técnicas, pitch de proyectos de IA y storytelling para evaluaciones académicas. Tu tarea es crear una presentación de video y una estructura de diapositivas para explicar el proyecto Daikoku a un público amplio, incluyendo personas sin experiencia técnica.

## Contexto del proyecto

Proyecto: Daikoku
Tipo: asistente académico basado en inteligencia artificial
Tecnología principal: LangGraph + RAG + embeddings + memoria por sesión
Objetivo: ayudar a estudiantes y usuarios a consultar material académico, documentos y apuntes sin leer manualmente todo el contenido.

## Idea central del proyecto

Daikoku es un agente académico que permite responder preguntas sobre documentos propios del usuario usando recuperación semántica local y, cuando hace falta, contexto externo. El sistema no responde solo con el conocimiento general del modelo, sino que primero busca evidencia en el material documentado del usuario y luego compone la respuesta final de forma contextualizada.

## Arquitectura clave

- Interfaz de usuario con Gradio
- Ingesta de documentos y textos
- Extracción y normalización de contenido
- Generación y almacenamiento de embeddings
- Búsqueda vectorial local con similitud semántica
- Enrutamiento con LangGraph
- Recuperación local y externa
- Memoria por sesión
- Finalización y respuesta final

## Componentes del sistema que deben explicarse

1. Qué es un RAG y por qué se usa en este proyecto
2. Qué es un embedding
3. Qué hace el router
4. Qué hace la recuperación local
5. Qué hace la recuperación externa y la API de Wikipedia
6. Qué es la memoria por sesión
7. Qué hace el finalizador
8. Por qué el proyecto es útil para estudiantes y docentes
9. Cómo se valida el sistema con pruebas y qué resultados tiene

## Objetivo de la presentación

La presentación debe:
- explicar el problema de forma clara
- mostrar cómo funciona la solución técnica
- describir la arquitectura y los módulos
- demostrar valor académico y práctico
- convencer de que el proyecto tiene una base sólida y está alineado con la rúbrica

## Audiencia

- profesores
- compañeros de curso
- evaluadores académicos
- personas con poco conocimiento técnico

## Estilo de la presentación

- clara
- concisa
- profesional
- didáctica
- con lenguaje técnico pero explicando conceptos de forma simple
- con énfasis en valor real del sistema

## Recomendación de formato de video

El video debe durar entre 3 y 5 minutos.
Debe tener una voz en off clara, con ritmo natural, y una narrativa que avance desde el problema hasta la solución.

## Estructura sugerida para el video

### Introducción (15-20 segundos)
- Presentar el problema: muchos documentos y mucha información dispersa.
- Explicar que la solución es un asistente que ayuda a responder preguntas con base documental.

### Problema y necesidad (20-30 segundos)
- Explicar que las personas no tienen tiempo de leer todo.
- Mostrar la necesidad de un sistema que entienda texto, recupere información relevante y responda con contexto.

### Solución propuesta (30-45 segundos)
- Explicar que Daikoku es un agente inteligente basado en RAG.
- Describir la idea central: consulta del usuario, recuperación de evidencia, respuesta contextualizada.

### Arquitectura técnica (45-60 segundos)
- Explicar el flujo: ingreso de documentos, embeddings, búsqueda, router, recuperación local, recuperación externa, finalizer.
- Mostrar simple diagrama o representación visual.

### Módulos clave (30-45 segundos)
- Router
- Recuperación local
- Recuperación externa
- Memoria por sesión

### Valor y beneficios (20-30 segundos)
- Ahorro de tiempo
- Respuestas más confiables
- Mejor uso del material académico
- Continuidad de conversación

### Validación y resultados (30-45 segundos)
- Explicar que hubo pruebas de validación del router, sesión, contexto, manejo de errores, etc.
- Mostrar la idea de que el proyecto está funcionando y cumple con el esquema de evaluación.

### Cierre (20-30 segundos)
- Resumen final del proyecto
- Enfatizar que es una base sólida para un sistema académico real y extensible

## Estructura sugerida para la presentación en PowerPoint

### Diapositiva 1: Título
- Título: Daikoku
- Subtítulo: Asistente académico con IA para consultar documentos
- Logo o imagen de IA + documentos + estudio

### Diapositiva 2: Problema
- Documentos largos y dispersos
- Dificultad para encontrar información relevante
- Necesidad de una herramienta que comprenda contexto y responda de forma útil

### Diapositiva 3: Solución propuesta
- Daikoku como asistente académico
- Enfoque basado en RAG
- Recuperación de contexto relevante + respuesta final

### Diapositiva 4: Arquitectura del sistema
- Diagrama del flujo del agente
- Mostrar router, local retrieval, external retrieval, finalizer

### Diapositiva 5: Componentes clave
- Embeddings
- Búsqueda semántica
- Memoria por sesión
- Herramienta externa (Wikipedia)

### Diapositiva 6: Flujo de funcionamiento
- Paso a paso del uso del sistema
- Ejemplo de pregunta y respuesta

### Diapositiva 7: Validación y pruebas
- Sección de pruebas del proyecto
- Casos cubiertos: router, contexto local, contexto externo, memoria, error, continuidad, dudas vacías

### Diapositiva 8: Resultados y cierre
- Qué aporta el proyecto
- Qué lo hace especial
- Conclusión final y agradecimiento

## Guía para la narración del video

El narrador debe seguir este patrón:
1. Presentar el contexto
2. Explicar el problema
3. Presentar la solución
4. Describir la arquitectura
5. Mostrar cómo funciona en la práctica
6. Explicar validación y valor del proyecto
7. Cerrar con impacto

## Reglas importantes

- No usar demasiada jerga sin explicar
- Explicar conceptos clave en lenguaje simple
- Mantener el foco en la utilidad práctica
- Definir claramente la diferencia entre contexto local y contexto externo
- Enfatizar que el proyecto tiene una base técnica y una lógica clara de evaluación

## Resultado final que debe entregar la IA

La IA debe generar:
- un guion de voz en off
- una estructura de diapositivas
- una guía visual para la presentación
- una narrativa más natural para video
- una versión más institucional para evaluación académica

## Prompt final para entregar a la IA

Genera una presentación técnica y didáctica del proyecto Daikoku, diseñada para un video de 3 a 5 minutos y para una presentación en PowerPoint. Debe explicar el problema, la solución propuesta, la arquitectura del sistema, los conceptos clave (RAG, embeddings, router, memoria, contexto externo), la utilidad del proyecto y la validación realizada. La audiencia es mixta: profesores, evaluadores y compañeros con diferente nivel técnico. Usa un lenguaje claro, profesional y didáctico. Incluye: guion de voz en off, estructura de diapositivas, mensajes visuales, tiempos de cada sección y tono de presentación. Haz que la presentación se vea sólida, moderna y orientada a una evaluación académica.
