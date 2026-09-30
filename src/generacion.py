from typing import Iterable


def generate_answer(question: str, context: Iterable[str] | None = None) -> str:
    context_text = " ".join(str(part) for part in (context or []))
    if not context_text:
        return f"No se encontró información suficiente para responder: {question}"

    condensed = context_text[:800]
    return (
        f"Con base en el material disponible, la respuesta a '{question}' es que "
        f"el contenido recuperado indica: {condensed}. En síntesis, la información relevante "
        "sugiere que el documento aborda este tema de manera directa y contextualizada."
    )
