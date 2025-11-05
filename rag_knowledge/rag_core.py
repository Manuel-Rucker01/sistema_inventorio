from llama_index.core.tools import FunctionTool
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.embeddings import resolve_embed_model

# Configuraciones y datos de RAG (Simulación)
DOCUMENTOS_RAG = [
    "La política de devoluciones establece un plazo de 30 días con el embalaje original.",
    "El procedimiento para daños en el envío requiere llenar el Formulario 34B y notificar al proveedor en 48 horas.",
]

# Inicializa el motor RAG de forma simple
def init_rag_system():
    # En un entorno real, usaríamos un modelo de embeddings real como BAAI/bge-small-en-v1.5
    # Aquí usamos un mock para simplicidad
    try:
        # Crea un índice vectorial simple a partir de los documentos de texto
        # Se necesita un modelo de embeddings aquí. LlamaIndex lo gestiona internamente
        index = VectorStoreIndex.from_documents(
            SimpleDirectoryReader(input_files=DOCUMENTOS_RAG).load_data()
        )
        return index.as_query_engine()
    except:
        # Fallback si SimpleDirectoryReader no puede cargar los strings directamente
        return None # Devuelve None si falla la simulación

@FunctionTool.from_defaults
def consulta_documentos(pregunta: str) -> str:
    """Usa esta herramienta para responder preguntas sobre políticas, manuales, o procedimientos que NO son datos de stock."""
    
    # Esta es una simulación del motor de consulta RAG
    if "política" in pregunta.lower() or "devoluciones" in pregunta.lower():
        return f"CONTEXTO RECUPERADO: La política de devoluciones establece un plazo de 30 días con el embalaje original."
    
    if "envío" in pregunta.lower() or "daños" in pregunta.lower():
        return f"CONTEXTO RECUPERADO: El procedimiento requiere llenar el Formulario 34B y notificar al proveedor en 48 horas."
        
    return "La información requerida no se encontró en la base de conocimientos documentales."