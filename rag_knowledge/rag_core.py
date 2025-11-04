from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings 
from langchain_core.tools import tool
from typing import List, Dict, Any

# 1. Base de Conocimiento RAG (Simulación - Fines de demostración)
# En un proyecto real, estos documentos se cargarían desde archivos en la carpeta docs/
DOCUMENTOS_RAG = [
    "La política de devoluciones establece un plazo de 30 días con el embalaje original.",
    "El procedimiento para daños en el envío requiere llenar el Formulario 34B y notificar al proveedor en 48 horas.",
]

# Inicializa la Base Vectorial (Simulación)
# Usaremos FakeEmbeddings y FAISS. Nota: FakeEmbeddings NO se usa en producción, es para testing.
vectorstore = FAISS.from_texts(DOCUMENTOS_RAG, FakeEmbeddings(size=5))
retriever = vectorstore.as_retriever()


@tool
def consulta_documentos(pregunta: str) -> str:
    """Usa esta herramienta para responder preguntas sobre políticas, manuales, o procedimientos que NO son datos de stock."""
    
    # Lógica de Recuperación (Retrieval):
    if "política" in pregunta.lower() or "procedimiento" in pregunta.lower():
        # Obtener los documentos más relevantes usando el retriever
        docs = retriever.get_relevant_documents(pregunta)
        contexto = "\n".join([doc.page_content for doc in docs])
        
        # IMPORTANTE: En la orquestación final, este 'contexto' se pasa al LLM para el NLG.
        return f"CONTEXTO RECUPERADO:\n{contexto}"
    
    return "La información requerida no se encontró en la base de conocimientos documentales."

# ----------------------------------------------------
# Nota: La lógica de la Cadena RAG (RetrievalQA) se moverá 
# al módulo de orquestación (agent_app.py) en la rama feature/agent-orchestration.
# ----------------------------------------------------