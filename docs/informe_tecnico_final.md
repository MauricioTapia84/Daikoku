# Informe técnico final: Daikoku

## 1. Resumen ejecutivo

Daikoku es un asistente académico basado en arquitectura RAG (Retrieval-Augmented Generation) que combina recuperación local de documentos, contexto externo y memoria de sesión para responder preguntas de forma más precisa y contextualizada. El sistema está pensado para ayudar a estudiantes, docentes y usuarios generales a consultar material académico sin necesidad de leer manualmente documentos extensos.

El proyecto se construye sobre una estructura modular que separa responsabilidades: ingreso y preparación de documentos, almacenamiento semántico, recuperación por similitud, enrutamiento del flujo, memoria persistente y generación final de respuestas. Además, incluye validaciones formales del estado del agente, manejo de errores y mecanismos de continuidad de conversación por sesión.

La propuesta no se limita a un chatbot básico: incorpora un diseño de agente con grafo de flujo (LangGraph), búsqueda semántica con embeddings y lógica de enrutamiento para decidir cuándo es necesario recuperar información local o externa. Este enfoque logra una respuesta más útil, más trazable y más cercana a una aplicación real de sistemas de IA aplicada a documentos.

---

## 2. Motivación y contexto

En entornos académicos y profesionales, la información suele estar dispersa en archivos, apuntes, PDFs, resúmenes y material docente. La dificultad no es solo encontrar contenido, sino identificar la parte relevante para una pregunta concreta y responder con contexto adecuado.

Un asistente basado simplemente en un modelo de lenguaje puede responder de manera útil, pero suele carecer de anchoring documental. Esto puede provocar que genere respuestas que parezcan correctas pero no estén basadas en el material real del usuario.

Daikoku resuelve esta limitación recuperando primero el contenido relevante del corpus del usuario y, cuando hace falta, complementando con información externa. De ese modo, la respuesta no se apoya solo en el conocimiento general del modelo, sino también en evidencia documentada.

---

## 3. Objetivos del proyecto

Los objetivos del proyecto son los siguientes:

1. Construir un asistente académico funcional para consultar documentos.
2. Recuperar información relevante por similitud semántica en vez de por palabras exactas.
3. Separar claramente los roles de recuperación local, recuperación externa y finalización.
4. Mantener memoria por sesión para continuidad de conversación.
5. Validar el flujo del agente y manejar errores sin bloquear la ejecución.
6. Documentar el proyecto con un enfoque técnico y comprensible para distintos perfiles.

---

## 4. Arquitectura general del sistema

El sistema se compone de varias capas interconectadas:

### 4.1. Capa de entrada y preparación de documentos
La primera etapa trata de transformar el contenido bruto en información utilizable para el sistema. En esta parte se realiza:

- lectura de archivos de texto o documentos compatibles
- limpieza y normalización de texto
- partición por fragmentos o chunks
- preparación del contenido para su indexación

### 4.2. Capa de embeddings y similitud
A continuación, el texto se representa mediante embeddings. Los embeddings son vectores numéricos que capturan el significado del contenido. Cuando el usuario pregunta algo, también se convierte esa pregunta en un vector y se compara con los vectores del corpus para recuperar los fragmentos más cercanos.

### 4.3. Capa de almacenamiento vectorial
El sistema guarda los textos y sus embeddings para recuperar información relevante. Esta capa se encarga de mantener una “base local” de contexto semántico y devolver resultados ordenados por relevancia.

### 4.4. Capa de orquestación con LangGraph
El agente no responde en una sola fase. El flujo se estructura en nodos con responsabilidades claras:

- router: decide si la consulta necesita contexto local, externo o ambos
- retrieve_context: obtiene evidencia del corpus local
- retrieve_external: consulta fuentes externas para complementar la respuesta
- finalizer: genera la respuesta final y persiste la memoria

Este enfoque hace al sistema más explicable, más robusto y más fácil de modificar.

### 4.5. Capa de memoria y persistencia
La conversación no se pierde entre turnos. El agente guarda el historial por sesión usando un identificador único. Esto permite mantener continuidad, responder preguntas de seguimiento y resumir información antigua si el historial crece demasiado.

### 4.6. Capa final de generación
La respuesta final se construye con el contexto recuperado. La idea es que el sistema responda con base en evidencia y no solo en la intuición general del modelo.

---

## 5. Qué es un RAG y por qué se usa en este proyecto

RAG significa Retrieval-Augmented Generation, o generación aumentada por recuperación. Es una técnica en la que un modelo de IA primero busca información útil en un conjunto de datos o documentos, y luego utiliza esa información para responder.

### ¿Por qué es útil?
- reduce respuestas inventadas
- mejora la base documental de la respuesta
- permite usar contenido específico del usuario
- hace más fácil integrar fuentes internas y externas

### Aplicación en Daikoku
En este proyecto, el usuario puede cargar documentos y luego preguntar sobre ellos. El agente recupera fragmentos relevantes del material del usuario y los usa para responder. Cuando la pregunta es conceptual o requiere apoyo adicional, también consulta una fuente externa como Wikipedia. Este diseño combina dos fuentes de conocimiento: la propia del usuario y la complementaria del entorno externo.

---

## 6. Qué es un embedding y por qué es importante

Un embedding es una representación matemática de un texto en un espacio vectorial. En lugar de depender únicamente de coincidencias textual exactas, el embedding intenta capturar el significado del contenido.

Por ejemplo, dos frases relacionadas sobre el mismo concepto estarán cercanas en ese espacio, aunque no compartan las mismas palabras exactas.

### Relación con la recuperación
Cuando el usuario hace una pregunta, esta pregunta también se convierte en un vector. Después, el sistema compara ese vector con los embeddings de los documentos del corpus y ordena los resultados por cercanía semántica. Así se obtiene contenido relevante aunque no haya coincidencias exactas de palabras.

### Valor práctico
Esto hace que la búsqueda sea mucho más inteligente que una búsqueda literal por texto. En contextos académicos, donde los conceptos pueden expresarse con sinónimos o reformulaciones, esta capacidad es esencial.

---

## 7. ¿Qué hace el router y por qué es importante?

El router es la parte del sistema que decide por qué camino debe avanzar la consulta dentro del grafo del agente.

### Función principal
El router analiza la intención de la consulta y decide si es más apropiado:

- usar contexto local del corpus del usuario
- usar contexto externo como información complementaria
- combinar ambos tipos de contexto

### ¿Por qué es importante?
Porque no todas las preguntas tienen la misma naturaleza. Una pregunta sobre un documento específico requiere evidencia local. Una pregunta conceptual puede requerir información general. El router hace que el sistema sea más eficiente, más transparente y más adaptable.

En este proyecto, el router está integrado dentro de la lógica de LangGraph, lo que permite que cada decisión esté formalizada y validada antes de continuar con la siguiente etapa.

---

## 8. ¿Qué es la memoria del agente?

La memoria del agente permite conservar el contexto de la conversación y mantener continuidad entre varias interacciones. En lugar de tratar cada pregunta como si fuera independiente, el sistema recuerda qué se ha preguntado antes y utiliza ese historial para responder mejor.

### Tipos de memoria
En este proyecto se trabaja con:

- memoria de sesión: persistente durante la misma conversación
- historial acotado: limitado para no saturar la memoria
- resumen del historial antiguo: para ahorrar espacio y conservar contexto relevante

### ¿Por qué importa?
La memoria ayuda a responder conversaciones del tipo:

- “¿Puedes repetirlo?”
- “¿Qué te acabo de preguntar?”
- “Quiero continuar con ese tema”

Esto hace que la experiencia del usuario sea más natural y más útil.

---

## 9. ¿Qué es la herramienta externa y por qué se usa?

La herramienta externa del proyecto es la consulta a Wikipedia. Se usa para complementar la recuperación local cuando la información necesaria no está presente en los documentos cargados por el usuario.

### Ventajas
- aporta definiciones o contexto general
- ayuda en preguntas conceptuales
- sirve como respaldo cuando el corpus local es insuficiente

### Limitaciones y control
La herramienta externa también se controla para evitar saturar la respuesta final con mucho contenido irrelevante. Se limitan los resultados y se normalizan los textos para mantener un contexto claro y útil. Además, si la conexión falla, el sistema responde sin romper el flujo.

---

## 10. Flujo del sistema paso a paso

El flujo general del proyecto puede describirse así:

1. El usuario escribe una pregunta.
2. El sistema valida la entrada para detectar si está vacía o ambigua.
3. El router decide si la consulta debe resolverse con contexto local, externo o ambos.
4. El agente recupera documentos o fragmentos relevantes.
5. Se combina el contexto recuperado con la intención de la consulta.
6. Se genera la respuesta final.
7. Se guarda la interacción en memoria por sesión.
8. La siguiente pregunta puede reutilizar ese historial.

Este flujo hace que el sistema se comporte de manera más parecida a un agente real que a una simple búsqueda de texto.

---

## 11. Estructura de archivos del proyecto

El proyecto principal está organizado en los siguientes módulos:

- `src/agente.py`: lógica principal del agente, validación del estado, enrutamiento, memoria y grafo de ejecución.
- `src/retrieval.py`: almacenamiento vectorial y búsqueda semántica.
- `src/embeddings.py`: generación de embeddings y comparación por similitud.
- `src/ingesta.py`: extracción, limpieza y fragmentación de texto.
- `src/generacion.py`: producción de respuesta final.
- `tests/test_daikoku.py`: validaciones del comportamiento del proyecto.
- `README.md`: documentación general y guía de uso.
- `docs/checklist_evaluacion_progreso.md`: seguimiento de la rúbrica.

Aunque cada archivo tiene una tarea específica, el sistema funciona como una cadena completa: ingestión → representación → recuperación → razonamiento → respuesta.

---

## 12. Validación y pruebas

El proyecto incorpora pruebas para comprobar el comportamiento real del agente, no solo su estructura. Estas pruebas cubren varias áreas:

- lógica del router
- recuperación local
- recuperación externa
- historial persistente
- continuidad de conversación
- manejo de preguntas vacías o ambiguas
- tratamiento de documentos no válidos
- comportamiento sin contexto

La evidencia actual del proyecto confirma que los principales comportamientos críticos del agente responden bien a la rúbrica y funcionan de forma estable.

---

## 13. Estado de cumplimiento frente a la rúbrica

El proyecto cumple con los requisitos principales de la propuesta: arquitectura formal, separación de nodos, validación del estado, manejo de errores, memoria por sesión y documentación técnica. Además, el sistema demuestra que la solución está alineada con el enfoque propuesto por el profesor y con los estándares de un proyecto académico con agentes de IA.

### Alineación con la rúbrica
- Estado formal del agente: cumplido
- Estructura del grafo y responsabilidades: cumplido
- Validación del flujo: cumplido
- Documentación de nodos e infraestructura: cumplido
- Recuperación local y semántica: cumplido
- Recuperación externa: cumplido
- Memoria del agente: cumplido
- Manejo de fallos y robustez: cumplido
- Documentación y explicación del proyecto: cumplido

---

## 14. Conclusión

Daikoku representa un ejemplo completo de un agente académico basado en RAG, con recuperación semántica, memoria, contexto externo y flujo modular. Su diseño permite entender tanto la lógica técnica como la utilidad práctica del sistema.

El proyecto no se limita a ser una demostración superficial de IA: se enfoca en una solución estructurada, validada y explicable. Esto lo hace adecuado para uso académico, documentación técnica, presentación ante evaluadores y ampliación futura.

La combinación de arquitectura clara, pruebas, memoria persistente y flujo de recuperación consolidan una base sólida para un sistema de IA útil, robusto y comprensible incluso para personas que se están iniciando en estos conceptos.
