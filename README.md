# Daikoku: Document Analysis and Intelligent Knowledge Organization for Key-concept Understanding

## Descripción

Daikoku es un asistente de estudio inteligente basado en un pipeline de Generación Aumentada por Recuperación (RAG). Permite a estudiantes cargar material académico en múltiples formatos (PDF, DOCX, XLSX, CSV), extraer su contenido, generar embeddings y consultar información contextualizada mediante un LLM.

## Estado del Proyecto

**Fase actual:** Planificación y diseño.
**Próximos pasos:** Implementación del pipeline en Google Colab.

## Tecnologías Propuestas

| Componente | Tecnología |
|:---|:---|
| Ingesta | MarkItDown |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | ChromaDB |
| LLM | Gemini 2.5 Flash (o Mistral API) |
| Interfaz | Gradio |
| Entorno | Google Colab / Python |

## Estructura del Repositorio
Daikoku/
├── README.md
├── docs/
│ ├── informe_EP1.pdf
│ └── diagramas/
├── src/

