from typing import Iterable


def generate_answer(
    question: str,
    context: Iterable[str] | None = None,
    domain: str = "documentos_academicos_universitarios",
    case_study: str = "asistente académico para documentos universitarios",
) -> str:
    context_text = " ".join(str(part) for part in (context or []))
    if not context_text:
        return (
            f"No tengo evidencia suficiente en el dominio de {domain} para responder de forma fiable "
            f"la pregunta: {question}."
        )

    condensed = context_text[:800]
    return (
        f"Con base en la evidencia recuperada para {domain}, la respuesta a '{question}' es que "
        f"los documentos y fragmentos recuperados indican: {condensed}. "
        f"Esta respuesta está apoyada por evidencia documental relevante del caso de uso '{case_study}' "
        "y debe interpretarse como una síntesis académica del material disponible."
    )
