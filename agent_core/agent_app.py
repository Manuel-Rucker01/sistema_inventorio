import os, sys
from llama_index.core.agent import ReActAgent # Usamos ReAct por su estabilidad
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
import asyncio 

try:
    # Obtenemos la ruta del archivo actual y retrocedemos un nivel ('/..')
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.join(ROOT_DIR, '..')
    
    # Agregamos la ruta superior al sistema (el directorio 'sistema_inventorio')
    if PARENT_DIR not in sys.path:
        sys.path.append(PARENT_DIR)
        
    print(f"DEBUG: Directorio raíz del proyecto añadido a PYTHONPATH: {PARENT_DIR}")
except Exception as e:
    print(f"Error al configurar PYTHONPATH: {e}")

# Importar funciones de los módulos locales
from database.db_tools import consultar_stock, actualizar_stock, buscar_similitud, crear_producto
from database.init_db import init_db
from rag_knowledge.rag_core import consulta_documentos # Importa la herramienta RAG

# --- 1. CONFIGURACIÓN DEL AGENTE ---

# 1.1 Conexión con Llama 3 (Ollama)
try:
    llm = Ollama(model="llama3", request_timeout=30.0)
except Exception as e:
    print(f"Error al conectar con Ollama. Asegúrate que esté corriendo. {e}")
    # Si Ollama falla, se usa un LLM simulado, pero requeriría un ToolRunner diferente.
    # Por simplicidad, el script termina si Ollama no está activo.
    exit()

# 1.2 Listado y Conversión de Herramientas
# Las herramientas DB son funciones normales; las convertimos a objetos FunctionTool
db_tools = [
    FunctionTool.from_defaults(fn=consultar_stock),
    FunctionTool.from_defaults(fn=actualizar_stock),
    FunctionTool.from_defaults(fn=buscar_similitud),
    FunctionTool.from_defaults(fn=crear_producto),
]

# La herramienta RAG (ya es un Tool en rag_core.py, o se define aquí si es más simple)
tools = db_tools + [consulta_documentos]

# 1.3 Definición del Prompt (El 'Comportamiento' del Agente)
SYSTEM_PROMPT = """
Eres un Agente de Gestión de Inventario inteligente y profesional. Tu tarea es asistir al empresario.
Tu proceso de decisión debe priorizar la precisión del inventario SQL.

Reglas de Oro:
1. Utiliza las herramientas de DB (consultar_stock, actualizar_stock, crear_producto, buscar_similitud) para cualquier solicitud de inventario en tiempo real.
2. Utiliza la herramienta 'consulta_documentos' para cualquier pregunta sobre políticas, manuales o procedimientos.
3. Responde siempre de forma clara y profesional, basándote ÚNICAMENTE en la salida de las herramientas.
"""

# 1.4 Creación del Agente (Usando ReAct, la forma más compatible)
agent = ReActAgent(
    tools=tools, 
    llm=llm, 
    verbose=True,
    system_prompt=SYSTEM_PROMPT
)


# --- 2. FUNCIÓN PRINCIPAL Y PRUEBAS ---

async def run_chatbot():
    print("Inicializando Base de Datos...")
    init_db() 
    
    print("\n" + "="*50)
    print("CHATBOT DE INVENTARIO HÍBRIDO CON LLAMA 3 (OLLAMA)")
    print("="*50 + "\n")

    # PRUEBA 1: Función Calling (Actualización de stock)
    print(">>> PRUEBA 1: Actualizar stock de Tornillo M4 (ACCIÓN)")
    response_update = await agent.run("Recibimos 80 Tornillos M4 x 10mm, añádelos.")
    print(f"\nRespuesta del Chatbot:\n{response_update}\n")

    # PRUEBA 2: Consulta RAG (Conocimiento)
    print(">>> PRUEBA 2: Consulta sobre una política (CONOCIMIENTO)")
    response_rag = await agent.run("¿Cuál es el procedimiento que debemos seguir al recibir un envío con daños?")
    print(f"\nRespuesta del Chatbot:\n{response_rag}\n")

if __name__ == "__main__":
    asyncio.run(run_chatbot())