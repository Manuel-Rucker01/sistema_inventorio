import sqlite3
import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from database.db_tools import consultar_stock, actualizar_stock, buscar_similitud, crear_producto
from rag_knowledge.rag_core import consulta_documentos, init_rag_system

# --- 1. CONFIGURACIÓN DEL SISTEMA ---

# 1.1 Conexión con Llama 3 (Ollama)
try:
    llm = Ollama(model="llama3", base_url="http://localhost:11434")
except Exception as e:
    print(f"Error al conectar con Ollama. Se usará un LLM de simulación: {e}")
    from langchain_community.llms import FakeListLLM
    # Se añade una respuesta para simular una llamada exitosa del Agente
    llm = FakeListLLM(responses=["Simulación: Llamada a herramienta exitosa"])

# 1.2 Definición del Prompt (El 'Comportamiento' del Agente)
SYSTEM_PROMPT = """
Eres un Agente de Gestión de Inventario inteligente y profesional. Tu tarea es asistir al empresario.

Reglas de Oro:
1. Utiliza las herramientas (consultar_stock, actualizar_stock) para cualquier solicitud de inventario en tiempo real (stock, ubicación, añadir/restar).
2. Utiliza la herramienta 'consulta_documentos' para cualquier pregunta sobre políticas, manuales o procedimientos.
3. Responde siempre de forma clara, profesional y amigable, utilizando la salida de las herramientas como única fuente de verdad.
4. Si una herramienta devuelve 'Error', informa del error de forma amigable.
"""

# 1.3 Listado de Todas las Herramientas
# El LLM ve esta lista y decide cuál usar.
tools = [consultar_stock, actualizar_stock, consulta_documentos, buscar_similitud, crear_producto]

# 1.4 Creación del Prompt Final para el Agente
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"), # Espacio que usa LangChain para el razonamiento
    ]
)

# 1.5 Creación y Ejecución del Agente
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- 2. FUNCIÓN PRINCIPAL Y PRUEBAS ---

def run_chatbot():
    # Asegurarse de que la base de datos se inicializa una vez
    # Importamos la función de inicialización de la DB desde la carpeta 'database'
    from database.init_db import init_db
    init_db() 
    
    # Inicializamos el sistema RAG
    # El init_rag_system debe ser una función en rag_core.py que inicialice la base vectorial.
    # init_rag_system() # Descomentar cuando esa función se añada en la rama RAG

    print("\n" + "="*50)
    print("🤖 CHATBOT DE INVENTARIO HÍBRIDO CON LLAMA 3 (OLLAMA)")
    print("="*50 + "\n")

    # Pruebas de funcionamiento (similares a las que teníamos antes)
    
    # Prueba 1: Actualizar stock (Función Calling)
    print(">>> PRUEBA 1: Actualizar stock de Tornillo M4")
    response_update = agent_executor.invoke({"input": "Recibimos 80 Tornillos M4 x 10mm, añádelos."})
    print(f"\nRespuesta del Chatbot:\n{response_update['output']}\n")

    # Prueba 2: Consulta de stock (Función Calling)
    print(">>> PRUEBA 2: Consulta de stock de Martillo Bicolor")
    response_query = agent_executor.invoke({"input": "¿Cuántos Martillos Bicolor 500g me quedan?"})
    print(f"\nRespuesta del Chatbot:\n{response_query['output']}\n")

    # Prueba 3: Consulta RAG (Conocimiento)
    print(">>> PRUEBA 3: Consulta sobre una política")
    response_rag = agent_executor.invoke({"input": "¿Cuál es el procedimiento que debemos seguir al recibir un envío con daños?"})
    print(f"\nRespuesta del Chatbot:\n{response_rag['output']}\n")


if __name__ == "__main__":
    run_chatbot()