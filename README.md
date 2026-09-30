# Daikoku

## Descripción general

Daikoku es un asistente académico inteligente orientado a responder preguntas a partir de documentos propios del usuario, combinando recuperación semántica local y contexto externo de Wikipedia. La idea principal es permitir que un estudiante, investigador o docente consulte material académico sin tener que revisar manualmente todo el contenido de un archivo largo.

El sistema integra varias capas:

- ingreso de documentos y textos
- extracción y normalización de contenido
- almacenamiento vectorial local
- recuperación por similitud semántica
- orquestación con LangGraph
- memoria de sesión por conversación
- respuesta final contextualizada
- interfaz de uso con Gradio

En su versión actual, el proyecto funciona como un agente RAG (Retrieval-Augmented Generation) con router, recuperación local, recuperación externa y finalización de la respuesta. Este enfoque lo acerca a un patrón de agente profesional con flujo estructurado y decisiones explícitas.

---

## Objetivo del proyecto

El proyecto busca ayudar a usuarios a comprender documentos complejos mediante un asistente que:

- responde preguntas sobre documentos cargados
- identifica contenido relevante dentro del material
- recupera información complementaria desde Wikipedia cuando la consulta lo requiere
- mantiene historial de la conversación por sesión
- ofrece una interfaz simple para usar el sistema sin necesidad de programación

---

## Casos de uso

Daikoku es útil para:

- estudiantes revisando apuntes, PDFs o resúmenes
- docentes buscando conceptos clave en material de clase
- usuarios que quieren consultar información sin leer todo el documento
- prototipos académicos de sistemas de IA orientados a documentación

---

## Arquitectura del sistema

El proyecto está estructurado en capas funcionales:

1. Interfaz de usuario

   - Gradio
   - Permite enviar preguntas e interactuar con el agente
2. Capa de ingreso de información

   - Documentos y texto libre
   - Se almacenan y luego se indexan para recuperación
3. Capa de extracción y normalización

   - `src/ingesta.py`
   - Convierte textos de entrada en chunks procesables
4. Capa de embeddings y similitud

   - `src/embeddings.py`
   - Genera vectores de representación del texto
   - Calcula similitud por coseno
5. Capa de almacenamiento vectorial

   - `src/retrieval.py`
   - Mantiene una colección local de documentos con embeddings
   - Permite buscar el contenido más similar a una consulta
6. Capa de orquestación del agente

   - `src/agente.py`
   - Implementa un flujo con LangGraph
   - Tiene un router, recuperación local, recuperación externa y finalizer
7. Capa de generación de respuesta

   - `src/generacion.py`
   - Produce la respuesta final usando el contexto recuperado
8. Persistencia de sesión

   - Se guarda historial de conversación por `session_id`
   - Permite continuidad dentro de la misma sesión

---

## Flujo de ejecución

### 1. Carga de documentos

El usuario puede:

- añadir documentos al sistema mediante la API del agente
- usar la interfaz Gradio e ingresar contenido adicional por línea
- invocar `agent.ingest_file()` o `agent.ingest_files()` desde código

### 2. Recuperación local

Cuando el usuario hace una consulta, el sistema:

- transforma la pregunta en un vector
- compara la consulta contra los documentos ya indexados
- selecciona los fragmentos más relevantes

### 3. Enrutamiento

El agente decide si la consulta debe ir por:

- contexto local si hay documentos relevantes
- contexto externo si la pregunta es conceptual o no tiene correspondencia local

Esto se hace en el nodo `router` del grafo de LangGraph.

### 4. Recuperación externa

Si el sistema decide usar contexto externo, consulta la API de Wikipedia en español o inglés y extrae resúmenes breves relevantes para la consulta.

### 5. Finalización

El nodo `finalizer`:

- combina contexto interno + externo
- genera la respuesta final
- agrega la interacción al historial de la sesión

---

## Estructura del repositorio

```text
Daikoku/
├── README.md
├── requirements.txt
├── main.py
├── docs/
│   └── (material de apoyo del proyecto)
├── src/
│   ├── agente.py
│   ├── embeddings.py
│   ├── generacion.py
│   ├── ingesta.py
│   └── retrieval.py
├── tests/
│   ├── test_daikoku.py
│   └── ejemplos/
│       └── preguntas_prueba.txt
└── .venv/   (si se crea localmente)
```

### Descripción de archivos clave

- `main.py`: punto de entrada de la interfaz Gradio
- `src/agente.py`: lógica del agente, router, finalizer, memoria y LangGraph
- `src/retrieval.py`: sistema de búsqueda vectorial local
- `src/embeddings.py`: generación de embeddings y similitud
- `src/generacion.py`: construcción de respuesta final
- `src/ingesta.py`: preparación y extracción de texto
- `tests/test_daikoku.py`: validaciones funcionales del proyecto

---

## Requisitos

### Requisitos mínimos

- Python 3.10 o superior
- Internet para consultas a Wikipedia
- Acceso a consola o terminal
- Dependencias del proyecto (se instalan desde `requirements.txt`)

### Dependencias principales

El proyecto usa:

- `gradio`
- `requests`
- `langgraph`
- `langchain`
- `langchain-core`
- `markitdown`
- `pypdf`
- `sentence-transformers`
- `pytest`/`unittest` para validaciones

La lista completa puede verse en [requirements.txt](requirements.txt).

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Daikoku
```

### 2. Crear entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si aparece este error:

```powershell
No se puede cargar el archivo ...\Activate.ps1 porque la ejecución de scripts está deshabilitada en este sistema
```

significa que la política de ejecución de PowerShell está bloqueando scripts. Para activar el entorno solo para la sesión actual, ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Esto permite ejecutar scripts temporalmente sin cambiar la política global del sistema.

En Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

En la mayoría de entornos Windows, la forma más fiable es usar el intérprete de Python del entorno virtual en lugar de invocar `pip.exe` directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Esto evita bloqueos de seguridad asociados a `pip.exe` en sistemas con políticas de aplicación o AppLocker.

> En algunos entornos Windows puede requerirse instalar con permisos adicionales o usar la ruta del ejecutable de Python del sistema. El proyecto fue validado en un entorno con Python 3.14.

### 4. Solución rápida para errores de seguridad en Windows

Si aparece este mensaje:

```powershell
Error al ejecutar el programa 'pip.exe': Una directiva de Control de aplicaciones bloqueó este archivo
```

la causa es la política de seguridad del equipo, no el proyecto. La solución recomendada es usar el intérprete de Python como referencia:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si además se bloquea la activación del entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

## Ejecución del proyecto

### Ejecutar la interfaz Gradio

```bash
python main.py
```

o, si estás usando el entorno virtual creado manualmente:

```powershell
.\.venv\Scripts\python.exe main.py
```

Esto levantará la interfaz del agente en el navegador. El usuario podrá:

- escribir preguntas
- añadir documentos o fragmentos adicionales
- interactuar con el sistema en una sesión compartida

### Ejecutar pruebas

```bash
python -m unittest tests.test_daikoku -q
```

o:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_daikoku -q
```

---

## Prompts de prueba

A continuación, algunos ejemplos de preguntas para validar el comportamiento del sistema con documentos académicos o de estudio.

### Preguntas generales

```text
¿De qué trata este documento?
¿Qué es un modelo de redes neuronales?
Resume en pocas palabras la idea principal del contenido.
Explica este concepto de forma sencilla.
¿Hay alguna definición clara de este tema?
```

### Preguntas orientadas a recuperación local

```text
¿Cuál es la diferencia entre machine learning y deep learning?
¿Qué mencionan los documentos sobre redes neuronales?
¿Dónde se habla del concepto principal del texto?
¿Qué ideas clave aparecen en el material?
¿Puedes resumir los puntos más relevantes?
```

### Preguntas de validación de memoria

```text
¿Qué acabamos de discutir?
Repite la respuesta anterior en una versión más breve.
¿Puedes explicarlo con un ejemplo?
```

### Preguntas para activar contexto externo

```text
¿Qué es una red neuronal?
Define aprendizaje automático.
¿Quién fue el creador de la inteligencia artificial moderna?
¿Qué es un concepto clave relacionado con este tema?
```

Estas preguntas permiten comprobar que el agente:

- recupera información del corpus local
- usa contexto externo cuando es necesario
- mantiene memoria en la misma sesión
- responde en un estilo útil para estudio y consulta académica

---

## Uso desde Python

También puede instanciar el agente directamente desde código:

```python
from src.agente import DaikokuAgent

agent = DaikokuAgent()
agent.add_documents([
    "Neural networks are computational models inspired by biological brains.",
    "Machine learning uses algorithms to detect patterns from examples."
])

respuesta = agent.answer("What are neural networks?", session_id="session_1")
print(respuesta)
```

También puede recuperar contexto externo manualmente:

```python
from src.agente import DaikokuAgent

agent = DaikokuAgent()
print(agent.buscar_contexto_externo("machine learning", top_k=2))
```

---

## Modo de funcionamiento del agente

El agente actual trabaja con un patrón de flujo tipo LangGraph:

```text
router
  ├── retrieve_context  → finalizer
  └── retrieve_external → finalizer
```

### Nodo router

Decide si la consulta debe resolverse:

- con documentos locales del sistema
- con un contexto externo adicional

### Nodo retrieve_context

Busca los textos semánticamente más similares en la base local.

### Nodo retrieve_external

Consulta Wikipedia para complementar la respuesta.

### Nodo finalizer

Genera la respuesta final y preserva la memoria de la sesión.

---

## Memoria persistente por sesión

El agente mantiene un historial por `session_id`:

```python
agent.answer("¿Qué es aprendizaje automático?", session_id="alumno_1")
agent.answer("Repite la respuesta anterior", session_id="alumno_1")
```

Esto permite que el sistema conserve el contexto de la conversación dentro de la misma sesión sin necesidad de resolverla desde cero.

---

## Variables de entorno y configuración

El proyecto admite una opción para activar embeddings semánticos más potentes si se desea utilizar una implementación basada en `sentence-transformers`:

```bash
set DAIKOKU_USE_SEMANTIC_MODEL=true
```

En PowerShell:

```powershell
$env:DAIKOKU_USE_SEMANTIC_MODEL = "true"
```

Esto activa el modelo semantic sentence-transformer cuando está disponible. Si no se configura, el sistema usa una estrategia de vectorización local basada en conceptos básicos para funcionar sin depender de modelos pesados.

---

## Limitaciones actuales

El proyecto es un prototipo técnico funcional con varios puntos relevantes a considerar:

- la generación de respuestas es ligera y orientada a contexto
- no depende de un proveedor externo de LLM para funcionar, aunque puede extenderse fácilmente
- la recuperación externa utiliza Wikipedia pública y requiere conexión a Internet
- el almacenamiento local es in-memory por defecto, no persistente en base de datos externa
- la extracción de documentos es útil para prototipos y uso académico básico

---

## Extensiones recomendadas

Entre mejoras futuras destacan:

- persistencia de historial en SQLite o archivos JSON
- integración con OpenAI, Azure OpenAI, GitHub Models u otros proveedores
- soporte más completo para PDFs, Word y Excel
- carga de múltiples documentos desde una carpeta
- mejoras en la limpieza y chunking de textos largos
- despliegue web con FastAPI o Streamlit

---

## Validación

El proyecto cuenta con pruebas funcionales en:

- `tests/test_daikoku.py`

Se verifican elementos como:

- recuperación local
- manejo de sesión
- agente con flujo de respuesta
- integración de contexto externo

Comando de validación:

```bash
python -m unittest tests.test_daikoku -q
```

---

## Resumen ejecutivo

Daikoku es un proyecto de asistente académico basado en RAG y LangGraph, pensado para responder preguntas sobre documentos del usuario con un enfoque práctico y docente. Su principal fortaleza es combinar:

- recuperación local semántica
- enrutamiento inteligente
- contexto externo de Wikipedia
- memoria de sesión
- interfaz simple con Gradio

Esto convierte al proyecto en una base sólida para aplicaciones de IA orientadas a documentación, educación y soporte de análisis de contenidos complejos.

---

## Licencia y uso

Este proyecto se entrega como base académica y técnica para investigación, aprendizaje y desarrollo. Puede ser reutilizado y extendido conforme a la intención del proyecto y la normativa de uso del entorno en el que se despliegue.
