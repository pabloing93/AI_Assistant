# .\gym-assistant-env\Scripts\activate

import streamlit as st
import logging # Added import for logging
import os  # Importar 'os' para verificar la existencia del directorio

# Configure logging to show only INFO level messages and above for a cleaner terminal output
# This helps in reducing the noise from DEBUG messages from various libraries.
logging.basicConfig(level=logging.INFO)
# You can also configure logging for specific noisy libraries if needed, for example:
# logging.getLogger("chromadb").setLevel(logging.WARNING)
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("openai").setLevel(logging.WARNING)

from backend import handle_query
from data_loader import load_data
from vector_store import initialize_vector_store

# Configuración de la página y estilos personalizados
st.set_page_config(page_title="DocuPy Bot", page_icon="🐍", layout="wide")

# --- LÓGICA DE INICIALIZACIÓN MEJORADA ---
# Definir la ruta del directorio del vector store
VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "vector_store")

# Solo crear el vector store si no existe
if not os.path.exists(VECTOR_STORE_DIR) or not os.listdir(VECTOR_STORE_DIR):
    print("\n=== Vector Store no encontrado. Iniciando creación por primera vez. ===")
    print("Este proceso puede tardar varios minutos y solo se ejecuta una vez.")
    
    data = load_data()
    if data:
        initialize_vector_store(data)
    else:
        print("ERROR: No se pudieron cargar los datos del PDF para crear el Vector Store.")
else:
    print(f"\n=== Vector Store encontrado en '{VECTOR_STORE_DIR}'. Saltando creación. ===")
# --- FIN DE LA LÓGICA DE INICIALIZACIÓN ---

# --- INICIALIZACIÓN DE ESTADÍSTICAS EN SESSION STATE ---
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "total_cost_usd" not in st.session_state:
    st.session_state.total_cost_usd = 0.0
if "last_query_info" not in st.session_state:
    st.session_state.last_query_info = {}

# --- BARRA LATERAL (SIDEBAR) PARA ESTADÍSTICAS ---
with st.sidebar:
    st.title("📊 Estadísticas de Uso")
    st.markdown("---")
    st.subheader("Última Consulta")
    if st.session_state.last_query_info:
        st.text(f"Tokens: {st.session_state.last_query_info.get('total_tokens', 0)}")
        st.text(f"Coste (USD): ${st.session_state.last_query_info.get('total_cost_usd', 0):.6f}")
    else:
        st.text("Aún no se han procesado consultas.")
    
    st.markdown("---")
    st.subheader("Total de la Sesión")
    st.text(f"Tokens: {st.session_state.total_tokens}")
    st.text(f"Coste (USD): ${st.session_state.total_cost_usd:.6f}")

st.title("DocuPy Bot 🐍")

# Inicializar historial en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "bot", 
        "content": """¡Hola! Soy **DocuPy Bot**.

Soy un asistente especializado en la documentación oficial de Python. Mi base de conocimientos es el documento que has cargado.

**Puedes preguntarme sobre:**
*   Sintaxis y uso de módulos estándar.
*   Explicaciones de funciones y clases.
*   Ejemplos de código que aparezcan en la documentación.

Simplemente escribe tu pregunta y buscaré la información más relevante para ti. ¿En qué puedo ayudarte?"""
    }]

# Input del usuario
user_input = st.chat_input("Pregunta sobre la documentación de Python...")

# Procesar mensaje del usuario
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Llamar al backend y procesar el diccionario de resultados
    result_data = handle_query(user_input, st.session_state.messages)
    response = result_data["answer"]
    st.session_state.messages.append({"role": "bot", "content": response})

    # Actualizar estadísticas en session_state
    st.session_state.total_tokens += result_data.get("total_tokens", 0)
    st.session_state.total_cost_usd += result_data.get("total_cost_usd", 0)
    st.session_state.last_query_info = {
        "total_tokens": result_data.get("total_tokens", 0),
        "total_cost_usd": result_data.get("total_cost_usd", 0)
    }
    
    # Forzar la re-ejecución para que la barra lateral se actualice inmediatamente
    st.rerun()

# Mostrar historial del chat con el método nativo de Streamlit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
