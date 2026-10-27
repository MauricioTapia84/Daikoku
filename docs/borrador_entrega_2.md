# Borrador de entrega final - Daikoku

## 1. Resumen ejecutivo

Daikoku es un asistente académico basado en un flujo RAG con LangGraph, recuperación semántica local, memoria persistente por sesión y contexto externo complementario. El proyecto tiene como objetivo permitir a estudiantes, docentes y usuarios consultar material académico con mayor rapidez y con evidencia documental, evitando depender solo del conocimiento general de un modelo de lenguaje.

El sistema actual presenta una arquitectura más formal y robusta que incluye validación del estado, separación de responsabilidades entre nodos, memoria de sesión, observabilidad por eventos y una capa de herramientas explícitas. Esto lo acerca a un patrón de agente real y más apropiado para una evaluación académica y técnica.

---

## 2. Objetivo del proyecto

El objetivo principal del proyecto es transformar un conjunto de documentos académicos en una base de consulta inteligente, donde el usuario pueda hacer preguntas y recibir respuestas contextualizadas, relevantes y trazables. La propuesta busca apoyar la comprensión del contenido sin reemplazar la lectura crítica de la fuente original.

---

## 3. Arquitectura general

La arquitectura se organiza en capas:

- ingest: carga y preparación de documentos
- embeddings: representación semántica del contenido
- vector store: almacenamiento y recuperación por similitud
- tool layer: herramientas explícitas del agente
- router: decisión sobre la ruta de la consulta
- retrieve local: búsqueda de evidencia en el corpus del usuario
- retrieve external: uso de Wikipedia como apoyo conceptual
- memory: historial y resumen por sesión
- observability: trazas y métricas del flujo
- finalizer: respuesta final y persistencia del estado

---

## 4. Estado actual del agente

El agente ya cuenta con una estructura formal que incluye un estado validado del flujo, definiciones de memoria, trazas por ejecución y un workflow organizado. Además, separa claramente tareas como routing, recuperación local, recuperación externa, memoria y finalización.

### Componentes clave

- AgentState: estado formal del agente
- ShortTermMemory: memoria reciente por sesión
- LongTermMemory: resumen persistente del historial
- VectorStore: almacenamiento vectorial con backend sólido
- Tool layer: conjunto de funciones explícitas del agente
- Router: decisión de ruta según la consulta
- Finalizer: respuesta final con contexto y historial

---

## 5. Herramientas explícitas del agente

El sistema incorpora una capa de herramientas bien definida:

- buscar_documentos
- buscar_en_wikipedia
- resolver_ambigüedad
- resumir_historial

Esto permite que la lógica del agente no dependa de una única operación opaca, sino que cada acción sea identificada, trazable y documentada con una finalidad concreta.

---

## 6. Recuperación local y semántica

La capa local recupera fragmentos relevantes del corpus del usuario mediante similitud semántica. Este punto es central, porque la respuesta final debe apoyarse en contenido real del documento y no solo en conocimiento general del modelo.

La mejora clave en esta versión es que el vector store contempla:

- backend FAISS cuando está disponible
- soporte Chroma cuando se habilita en el entorno
- fallback seguro a un índice local en memoria

Esto hace que la capa vectorial sea más estándar, más robusta y más alineada con un flujo profesional.

---

## 7. Recuperación externa

Cuando la consulta no puede resolverse solo con el material local, el agente usa una fuente externa complementaria. La estrategia actual se apoya en Wikipedia para entregar definiciones y contexto conceptual útil.

Este componente es importante porque permite atender preguntas conceptuales sin forzar al usuario a cargar todos los documentos necesarios. La lógica además incluye manejo de errores para evitar que la respuesta falle si la fuente externa no responde adecuadamente.

---

## 8. Memoria del agente

La memoria por sesión es un pilar esencial del sistema. El agente conserva el historial reciente y genera un resumen para no saturar la conversación ni perder el hilo contextual.

Esto mejora la continuidad del diálogo y permite responder preguntas del tipo:

- repite la respuesta
- ¿de qué hablabas antes?
- amplia la información anterior

La memoria se persiste localmente y se combina con la respuesta final para mantener coherencia entre turnos.

---

## 9. Observabilidad y trazabilidad

La observabilidad es una mejora importante del proyecto. El agente registra eventos como:

- decisiones del router
- selección de herramientas
- contexto recuperado
- finalización de la respuesta
- estado de la sesión
- métricas relevantes del flujo

Esto hace que la arquitectura sea más transparente, más comparable con un entorno real y más diagnóstica en caso de error o comportamiento inesperado.

---

## 10. Validación, benchmark y calidad

El sistema incluye validación del flujo y benchmark mínimo para evaluar la calidad de la recuperación. Las métricas principales incluyen:

- result_count
- top_score
- avg_score
- relevant
- index_summary
- backend
- latency_ms

Estas métricas permiten comprobar si la búsqueda semántica devuelve respuestas útiles y si el corpus cumple con la intención del usuario.

---

## 11. Mejoras frente al estado inicial

El proyecto ya incorporó varias mejoras clave respecto a una versión más básica:

- estado formal del agente
- separación más clara entre nodos
- metadata documental enriquecida
- memoria por sesión persistente
- tool layer explícito
- observabilidad
- backend vectorial más estándar
- benchmark de recuperación
- dominio académico mejor definido
- respuestas finales con evidencia documental

Esto lo acerca mucho más a un agente de IA con diseño académico y técnico avanzado.

---

## 12. Estado de cumplimiento

El proyecto se encuentra en una etapa muy sólida para entrega académica. Tiene una base funcional, una arquitectura razonable, flujo con enrutamiento y recuperación semántica, memoria, validación y documentación técnica.

Se alinea claramente con la lógica de ejemplos de agentes académicos más formales, con la diferencia de que aún puede mejorarse en madurez operativa, especialización de dominio y formalización del benchmark comparativo.

---

## 13. Conclusión

Daikoku ya no es solo un prototipo de RAG. Es un proyecto con estructura, flujo, memoria, trazabilidad y propósito académico bien definido. La propuesta es sólida, útil y alineada con las expectativas de un trabajo de IA aplicada a documentos.

La etapa final recomendada es reforzar la presentación, dejar la documentación técnica lista para entrega y cerrar la comparación con el estándar de referencia para mostrar de forma explícita la calidad del trabajo realizado.
