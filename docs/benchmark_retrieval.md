# Benchmark de recuperación semántica

## Objetivo

Este documento define una mínima batería de validación para medir la calidad de la recuperación local del agente Daikoku. La idea es evaluar si la búsqueda retorna resultados relevantes, ordenados y útiles para cada consulta típica del sistema.

## Consultas de prueba

1. "what are neural networks"
2. "how do machine learning models learn from data"
3. "what is deep learning"
4. "what is a chatbot"
5. "why is retrieval important in ai systems"

## Criterios de evaluación

- `result_count`: cantidad de fragmentos recuperados
- `top_score`: puntaje del mejor resultado
- `avg_score`: promedio de relevancia
- `relevant`: si el mejor resultado supera el umbral mínimo
- `index_summary`: resumen del índice local
- `backend`: backend activo utilizado por la búsqueda
- `latency_ms`: tiempo de respuesta de la query

## Métricas formales recomendadas para la siguiente etapa

Para llevar el benchmark a un nivel más académico, la siguiente evolución del proyecto debería incluir:

- `Precision@k`: proporción de resultados relevantes entre los `k` recuperados
- `Recall@k`: proporción de documentos relevantes recuperados sobre el total disponible
- `MRR` (Mean Reciprocal Rank): calidad del ordenamiento del primer resultado relevante
- `nDCG@k`: calidad del ranking cuando hay varios resultados relevantes con diferentes niveles de importancia
- `latencia promedio`: tiempo por query y variabilidad entre ejecuciones

## Reglas sugeridas

- para cada consulta, evaluar `top_k=3`
- usar `min_score=0.0` como base de comparación
- registrar si el resultado principal es compatible con la intención de la consulta
- anotar si falta contexto o si la consulta es demasiado general
- documentar el backend activo para cada prueba para comparar calidad y rapidez entre implementaciones

## Validación de latencia y comparabilidad por backend

La evaluación del backend vectorial se realiza con la función `VectorStore.compare_backends(...)`, que ejecuta la misma batería de queries sobre cada backend disponible y devuelve, por backend:

- `backend`: nombre del backend evaluado
- `avg_latency_ms`: latencia promedio por query
- `avg_top_score`: score medio del mejor resultado
- `result_count`: cantidad total de resultados recuperados
- `evaluations`: detalle por consulta, incluyendo `latency_ms`, `top_score` y `relevant`

Esto permite comprobar dos aspectos clave del 11.1:

1. Medir latencia de indexación y query por backend: el benchmark registra la latencia de cada query y luego promedia la respuesta por backend.
2. Validar comparabilidad entre backends: usando la misma query sobre cada backend, se compara si el ranking y la relevancia del mejor resultado permanecen coherentes.

En la práctica, la comparación se utiliza para asegurar que FAISS, Chroma y el fallback in-memory no solo sean funcionales, sino también comparables en términos de calidad y velocidad.

## Comparación por `top_k` y tamaño de chunk

Para el nivel 11.2, la evaluación también incluye dos comparaciones formales:

- `VectorStore.compare_top_k(...)`: recorre distintos valores de `top_k` y mide la variación en calidad y latencia de la recuperación.
- `VectorStore.compare_chunk_sizes(...)`: reconstruye la misma base documental con distintos tamaños de chunk y compara cómo cambia la relevancia del ranking.

Esto permite responder dos preguntas clave:

- ¿Qué tan sensible es la recuperación a la cantidad de documentos devueltos?
- ¿Qué tamaño de chunk mejora mejor la relación entre precisión y contexto útil?

## Resultado esperado

Se espera que:

- consultas específicas devuelvan al menos un resultado relevante
- consultas vagas no generen falsa confianza
- el top result tenga un score razonable y consistente
- el índice local mantenga metadata útil para cada fragmento

## Uso desde código

```python
from src.agente import DaikokuAgent

agent = DaikokuAgent()
agent.add_documents([
    "Neural networks learn patterns from data using layers and weights.",
    "Machine learning is a field focused on learning from examples.",
    "Deep learning uses layered neural networks to model complex patterns.",
])

benchmark = agent.benchmark_retrieval([
    "what are neural networks",
    "how do machine learning models learn from data",
    "what is deep learning",
], top_k=3, min_score=0.0)
print(benchmark)
```

## Observación

Este benchmark es una capa mínima de evaluación de calidad, útil para hacer el proyecto más formal y más comparable con un estándar académico de recuperación semántica.
