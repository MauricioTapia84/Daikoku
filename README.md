# Daikoku

**Document Analysis and Intelligent Knowledge Organization for Key-concept Understanding**

Asistente de estudio inteligente basado en un pipeline de Generación Aumentada por Recuperación (RAG), diseñado para apoyar a estudiantes de educación superior en la gestión, consulta y comprensión de material académico digital.

---

## 📋 Descripción

Daikoku es un proyecto académico en desarrollo, ideado por estudiantes de **Duoc UC** para abordar un problema real: la sobrecarga de información académica. Los estudiantes reciben grandes volúmenes de material (apuntes, PDFs, presentaciones, planillas) en períodos acotados, lo que dificulta su lectura completa, la priorización de contenidos clave y la comprensión profunda de los temas.

Daikoku propone un asistente que:

- Recibe documentos en múltiples formatos (PDF, DOCX, XLSX, CSV).
- Extrae y segmenta su contenido.
- Genera embeddings y los almacena en una base vectorial.
- Recupera los fragmentos más relevantes ante una consulta.
- Genera respuestas contextualizadas mediante un LLM.
- Enriquece las respuestas con una fuente externa controlada (Wikipedia).

---

## 🎯 Objetivos

### Objetivo General

Diseñar e implementar un asistente inteligente que permita a estudiantes de educación superior procesar, consultar y comprender material académico de manera eficiente, mediante la integración de modelos de lenguaje de gran tamaño (LLM) y técnicas de Generación Aumentada por Recuperación (RAG).

### Objetivos Específicos

1. Procesar archivos PDF, DOCX, XLSX y CSV, convirtiéndolos a una representación textual normalizada.
2. Segmentar el contenido y asociar metadatos de origen para habilitar recuperación semántica.
3. Responder preguntas utilizando prioritariamente fragmentos recuperados desde los documentos cargados.
4. Generar resúmenes y explicaciones simplificadas manteniendo relación explícita con las fuentes.
5. Incorporar una fuente externa controlada como respaldo complementario cuando la consulta lo requiera.

---

## 🏗️ Arquitectura de la Solución

El sistema se compone de las siguientes capas:

| Capa | Componente | Tecnología | Función |
|:---|:---|:---|:---|
| **Interfaz** | UI de carga y consulta | Gradio | Permite al usuario cargar archivos, seleccionar acciones y formular consultas. |
| **Ingesta** | Conversión de documentos | MarkItDown | Convierte PDF, DOCX, XLSX y CSV a Markdown procesable. |
| **Procesamiento** | Segmentación | Python / splitter | Divide el texto en fragmentos con solapamiento y metadatos. |
| **Embeddings** | Vectorización | paraphrase-multilingual-MiniLM-L12-v2 | Genera vectores multilingües de 384 dimensiones. |
| **Almacenamiento** | Base vectorial | ChromaDB | Almacena embeddings, texto y metadatos; permite búsqueda por similitud. |
| **Recuperación** | Retriever interno | ChromaDB | Recupera fragmentos relevantes de los documentos cargados. |
| **Recuperación** | Retriever externo | MediaWiki Action API (Wikipedia) | Recupera contexto complementario etiquetado como fuente externa. |
| **Orquestación** | Agente / Router | Python / LangChain | Clasifica la intención del usuario y selecciona la herramienta correspondiente. |
| **Generación** | LLM | Mistral API | Genera respuestas contextualizadas basadas en el contexto recuperado. |
| **Salida** | Formateador | Python | Devuelve la respuesta junto con las fuentes utilizadas. |

---

## 🔄 Flujo del Pipeline RAG

### Fase 1: Indexación

1. El usuario carga uno o más archivos.
2. MarkItDown convierte el contenido a Markdown.
3. El texto se limpia y divide en fragmentos (chunks).
4. Cada fragmento recibe un identificador y metadatos de origen.
5. El modelo de embeddings genera vectores.
6. Los vectores se almacenan en ChromaDB.

### Fase 2: Consulta

1. El usuario formula una pregunta.
2. La pregunta se convierte al mismo espacio vectorial.
3. El retriever busca los fragmentos más similares (top-k).
4. Si corresponde, se recupera contexto externo (Wikipedia).
5. El constructor de prompt combina instrucción + consulta + contexto.
6. El LLM genera la respuesta.
7. La respuesta se devuelve al usuario junto con las fuentes.

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología |
|:---|:---|
| Lenguaje | Python 3.10+ |
| Entorno | Google Colab |
| Ingesta | MarkItDown |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | ChromaDB |
| LLM | Mistral API |
| Fuente externa | MediaWiki Action API (Wikipedia) |
| Interfaz | Gradio |
| Orquestación | Python / LangChain (opcional) |

---

## 📁 Estructura del Repositorio
Daikoku/
├── README.md
├── docs/
│ ├── informe_EP1.pdf
│ ├── diagrama_flujo_rag.png
│ └── diagrama_arquitectura.png
├── src/
│ ├── ingesta.py
│ ├── embeddings.py
│ ├── retrieval.py
│ ├── generacion.py
│ └── agente.py
├── tests/
│ └── ejemplos/
│ ├── documento_prueba.pdf
│ └── preguntas_prueba.txt
└── requirements.txt


---

## ⚙️ Instalación

### Requisitos previos

- Python 3.10 o superior.
- Cuenta en Google Colab (o entorno local con Jupyter).
- API key de Mistral (obtener en https://console.mistral.ai/).

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/MauricioTapia84/Daikoku.git
cd Daikoku

# Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt