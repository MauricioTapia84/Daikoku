import gradio as gr

from src.agente import DaikokuAgent

agent = DaikokuAgent()


def handle_chat(message, history, documentos):
    if documentos.strip():
        docs = [part.strip() for part in documentos.splitlines() if part.strip()]
        agent.add_documents(docs)

    if not message or not message.strip():
        return "Escribe una pregunta para comenzar."

    return agent.answer(message, session_id="gradio-chat")


def main():
    sample = [
        "Neural networks are computational models inspired by biological brains. They learn patterns from data by adjusting weights.",
        "Machine learning uses algorithms to detect patterns and make predictions from examples.",
    ]
    agent.add_documents(sample)

    demo = gr.ChatInterface(
        fn=handle_chat,
        additional_inputs=[
            gr.Textbox(
                label="Documentos adicionales (uno por línea)",
                placeholder="Pega contenido académico aquí...",
                lines=6,
            )
        ],
        title="Daikoku Agent",
        description="Asistente académico con LangGraph, recuperación local y contexto externo de Wikipedia.",
    )
    demo.launch()


if __name__ == "__main__":
    main()
