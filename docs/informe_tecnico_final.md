# Informe técnico final: Daikoku

## 1. Resumen ejecutivo

Daikoku es un asistente académico orientado a responder preguntas sobre documentos propios del usuario mediante un flujo RAG con recuperación semántica, memoria por sesión y orquestación explícita. El sistema combina un agente con LangGraph, un backend vectorial local y una capa de recuperación externa para complementar la evidencia cuando el material del usuario no cubre la consulta.

En su estado actual, el proyecto está diseñado como un asistente académico realista para apoyar la consulta, comparación y comprensión de textos, apuntes, resúmenes y documentación universitaria. El valor del sistema no radica solo en responder preguntas, sino en hacerlo con evidencia documental, contexto útil y trazabilidad del proceso.

La solución actual incorpora:

- validación formal del estado del agente
- tool layer explícito
- router, retrieval y finalizer con responsabilidades bien definidas
- memoria por sesión y resumen persistente
- backend vectorial basado en FAISS con fallback seguro
- observabilidad por evento y trazas por ejecución
- benchmark comparativo para recuperación semántica
- respuestas finales con evidencia documental explícita

Esto acerca el proyecto a un patrón de agente más maduro, con arquitectura clara, rigor técnico y orientación académica.

---

## 2. Motivación y problema a resolver

Los estudiantes, docentes y usuarios académicos trabajan frecuentemente con colecciones grandes y heterogéneas de documentos: apuntes, PDF, artículos, resúmenes y material docente. El problema no es solo localizar información, sino identificar la parte relevante que responde la pregunta concreta y hacerlo con contexto útil.

Un modelo de lenguaje aislado puede responder de forma plausible, pero no garantiza que la información provenga del material del usuario. Daikoku corrige esa limitación al recuperar primero fragmentos del corpus local y, cuando la consulta lo requiere, añadir contexto externo de apoyo conceptual o definicional.

---

## 3. Objetivos del proyecto

1. Construir un asistente académico funcional para documentos propios del usuario.
2. Recuperar información relevante por similitud semántica.
3. Separar responsabilidades claras entre router, retrieval, memoria, generación y observabilidad.
4. Mantener memoria por sesión para continuidad de la conversación.
5. Mejorar la robustez frente a preguntas vacías, ambiguas o sin contexto local.
6. Validar y documentar el flujo del agente con enfoque técnico y académico.

---

## 4. Arquitectura del sistema

El sistema se organiza en capas funcionales.

### 4.1. Entrada y preparación del contenido
La capa inicial procesa y normaliza los documentos para que puedan usarse de manera reproducible. Esto incluye limpieza de texto, normalización y fragmentación del contenido.

### 4.2. Representación semántica
Los textos se convierten en vectores mediante embeddings, lo que permite comparar queries con documentos por similitud semántica, no solo por coincidencia léxica.

### 4.3. Vector store
La capa vectorial usa FAISS cuando está disponible y cuenta con un fallback seguro en memoria. Esto mejora la estabilidad del sistema y evita depender de una sola estrategia de recuperación.

### 4.4. Tool layer
El agente incluye una capa de herramientas explícitas:

- buscar_documentos
- buscar_en_wikipedia
- resolver_ambigüedad
- resumir_historial

Esto hace más clara la separación entre decisión del agente y ejecución concreta de una acción.

### 4.5. Orquestación con LangGraph
La orquestación sigue un flujo claro:

- router: decide si la consulta requiere contexto local o externo
- tool layer: determina la herramienta adecuada
- retrieve_context: recupera evidencia de documentos locales
- retrieve_external: consulta contexto externo complementario
- memory: recupera y resume la sesión
- observability: registra el estado del flujo
- finalizer: genera la respuesta final y persiste la memoria

Este diseño aumenta la trazabilidad y hace al agente más cercano a un sistema con lógica de producción.

---

## 5. Memoria, trazabilidad y observabilidad

El proyecto incorpora memoria por sesión con resumen persistente para mantener el hilo de la conversación sin saturar el contexto. La gestión de memoria incluye:

- historial corto por sesión
- deduplicación de mensajes repetidos
- resumen persistente
- límite de longitud para mantener la conversación estable

La capa de observabilidad registra eventos clave del flujo, con identificadores por ejecución (`trace_id`) y por sesión (`session_id`). Esto permite responder preguntas como:

- ¿qué ruta eligió el router?
- ¿qué herramienta se ejecutó?
- ¿qué contexto local o externo se usó?
- ¿cuál fue el backend vectorial activo?
- ¿qué longitud tuvo la respuesta final?

Estas trazas mejoran la diagnóstica del sistema y permiten evaluarlo con mayor rigor.

---

## 6. Recuperación local y externa

### Recuperación local
La capa local usa similitud semántica para recuperar fragmentos relevantes del corpus del usuario. Esta es la base principal del sistema, porque la respuesta final debe fundamentarse en información contenida en los documentos del usuario.

### Recuperación externa
Cuando la consulta es conceptual, general o no está cubierta por el material local, el agente usa una fuente externa complementaria, en este caso Wikipedia. Se aplica filtrado de relevancia para evitar introducir contexto genérico o poco útil.

La combinación de recuperación local y externa mejora la calidad del sistema ante distintos tipos de consulta.

---

## 7. Dominio y caso de uso

El proyecto se especializa como asistente académico para documentos universitarios y de estudio. Esto es importante porque define mejor su utilidad y evita presentarlo como un sistema totalmente generalista.

El caso de uso principal es:

- consulta sobre apuntes, resúmenes y material universitario
- apoyo a la comprensión de contenidos
- recuperación semántica de documentos estudiados
- respuesta contextualizada con evidencia documental

Esa especialización mejora la claridad del proyecto y su alineación con el caso de uso académico evaluado por el profesor.

---

## 8. Validación, robustez y pruebas

El agente incorpora validación del estado para prevenir errores de flujo y sostiene un comportamiento más robusto frente a casos complejos:

- preguntas vacías
- consultas ambiguas
- documentos no procesables
- resultados sin contexto relevante
- fallos de conexión a la API externa
- memoria saturada o historial repetitivo
- respuestas sin evidencia suficiente

Además, el sistema cuenta con pruebas automatizadas para validar el comportamiento real del flujo, la memoria, la recuperación local, la recuperación externa y la continuidad de conversación.

---

## 9. Benchmark de recuperación

El proyecto incorpora un enfoque de benchmark formal para evaluar la calidad de la recuperación semántica. Este componente permite medir la efectividad del sistema de forma reproducible.

Las métricas principales que se manejan son:

- result_count
- top_score
- avg_score
- relevant
- index_summary
- backend
- latency_ms

También incluye comparaciones por:

- backend activo
- `top_k`
- tamaño de chunk
- flujo de consultas repetidas

Esto convierte la recuperación semántica en una capa medible y comparable, y la acerca a estándares metodológicos más formales.

---

## 10. Ejecución y validación

El proyecto corre en un entorno virtual del repositorio y se valida mediante la suite de pruebas en `tests/test_daikoku.py`.

### Ejecución recomendada

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest tests.test_daikoku -q
```

### Ruta alternativa cuando el terminal del editor falla

```python
import subprocess
py = r"C:\Users\admin\Documents\GitHub\Daikoku\.venv\Scripts\python.exe"
subprocess.run([py, "-m", "unittest", "tests.test_daikoku", "-q"], cwd=r"C:\Users\admin\Documents\GitHub\Daikoku")
```

---

## 11. Estado final de cumplimiento

El proyecto se encuentra en un estado muy sólido para entrega académica. Tiene base funcional, arquitectura modular, flujo con routing, recuperación local y externa, memoria persistente, observabilidad y validación.

Su fortaleza principal es la combinación de:

- estructura del agente clara
- orientación académica y documental
- evidencia recuperada en la respuesta final
- calidad semántica y validación del flujo
- trazabilidad por sesión y ejecución

La diferencia respecto a un sistema completamente industrial aún queda en madurez operativa y exportación formal de métricas comparativas, pero el proyecto ya está muy cercano a la calidad esperada para una entrega final de nivel académico alto.

---

## 12. Conclusión

Daikoku ya no es un prototipo básico de RAG. Es un proyecto con estructura, flujo, memoria, trazabilidad, validación y propósito definido. Su enfoque combina evidencia documental, recuperación semántica y continuidad de conversación en un flujo ordenado y explicable.

El proyecto se presenta como una solución sólida para consultar documentos académicos con apoyo documental, trazabilidad y mejor calidad de respuesta, y se encuentra muy bien alineado con una entrega final técnica y académica.
