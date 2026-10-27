# Observabilidad de producción para Daikoku

## Objetivo

La observabilidad del agente permite diagnosticar el comportamiento del flujo en producción con una vista clara de cada decisión ejecutada por el router, el retrieval local, la recuperación externa, la memoria y el finalizer.

La intención no es solo registrar logs, sino poder responder preguntas como:

- ¿qué ruta eligió el agente para esta consulta?
- ¿qué contexto local y externo se usó?
- ¿cómo se persistió la sesión y el historial?
- ¿qué tan largo fue el contexto usado para producir la respuesta?
- ¿qué trazabilidad queda asociada a esta ejecución?

## Identificadores clave

Cada ejecución del grafo incluye:

- `session_id`: identifica la conversación del usuario
- `trace_id`: identifica una ejecución concreta del flujo
- `tool_name`: herramienta elegida por la capa de routing
- `route`: valor del router (`retrieve` o `external`)

Esto hace que cada respuesta pueda revisarse como una ejecución aislada dentro del comportamiento general del sistema.

## Eventos del flujo

El agente registra eventos como:

- `router_decision`
- `tool_layer`
- `local_retrieval`
- `external_retrieval`
- `memory_snapshot`
- `observability`
- `finalizer_output`
- `benchmark_retrieval`

Cada evento se persiste en la estructura de observabilidad del agente y se expone en logs con el payload asociado.

## Estructura de un payload

Un ejemplo de payload típico es:

```python
{
  "event": "observability",
  "domain": "documentos_academicos_universitarios",
  "case_study": "asistente académico para documentos universitarios",
  "trace_id": "session_1-20261027195734516660",
  "session_id": "session_1",
  "route": "external",
  "tool_name": "buscar_en_wikipedia",
  "context_count": 1,
  "external_context_count": 0,
  "vector_backend": "faiss",
}
```

Esto permite auditar el comportamiento del agente sin depender únicamente de la salida final del usuario.

## Memoria y sesión

La persistencia de la memoria por sesión se guarda en disco dentro del directorio `data/sessions/`, con un historial acotado y un resumen persistente que evita saturar la ventana del sistema.

La política actual combina:

- memoria corta por sesión (`short_term_history`)
- resumen persistente (`memory_summary`)
- deduplicación de contenidos repetidos
- acotación del historial para mantener un flujo estable

## Benchmark y medición de calidad

La observabilidad no se limita al flujo de la conversación; también está acoplada a la evaluación del sistema. El benchmark registra:

- latencia por query
- score del mejor resultado
- promedio de score
- número de resultados recuperados
- backend activo utilizado
- comparación entre distintos valores de `top_k` y tamaños de chunk

Esto hace que la evaluación de relevancia y rendimiento sea formal, reproducible y comparable.

## Recomendación final

El patrón actual deja el proyecto muy alineado con un sistema académico de tipo producción: el agente no solo responde, sino que explica cómo llegó a esa respuesta y qué evidencia utilizó para hacerlo.

Como siguiente refinamiento, se recomienda mantener esta trazabilidad en cada sesión y exportarla a un dashboard o archivo de auditoría para análisis longitudinal del rendimiento.
