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

# ----------------- START Whatsapp notification improvment

import re
import requests
from twilio.rest import Client
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)

TWILIO_SID = config["twilio_account_sid"]
TWILIO_TOKEN = config["twilio_auth_token"]
TWILIO_FROM = config["twilio_whatsapp_from"]
ADMIN_NUMBER = config["admin_number"]

def send_whatsapp_message(to_number, message):
    try:
        print(TWILIO_FROM)
        print(message)
        print(to_number)
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        print(client)
        message = client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=to_number
        )
        return True
    except Exception as e:
        print(f"Error sending WhatsApp: {e}")
        return False

def validate_whatsapp_number(number):
    # Accept formats like +54911xxxxxxx
    pattern = r"^\+54\d{9,11}$"
    return re.match(pattern, number)

if "awaiting_whatsapp" not in st.session_state:
    st.session_state.awaiting_whatsapp = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""
if "whatsapp_prompt_sent" not in st.session_state:
    st.session_state.whatsapp_prompt_sent = False

# ----------------- END Whatsapp notification improvment

# Configuración de la página y estilos personalizados
st.set_page_config(page_title="Ayudín Bot", page_icon="🤖", layout="wide")

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

st.title("Ayudín Bot 🤖")

# Inicializar historial en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "bot", 
        "content": """¡Hola! Soy **Ayudín**, tu asesor virtual de Econotodo.

Mi base de conocimientos está basado en información comercial actualizada.

**Puedes preguntarme sobre:**
*   Horarios de atención.
*   Disponibilidad de productos.
*   Promociones.
*   Medios de pago.

¿En qué puedo ayudarte?"""
    }]

# Input del usuario
if not st.session_state.awaiting_whatsapp:
    user_input = st.chat_input("Hola quiero saber si tenes azucar y cuanto sale")
else:
    user_input = st.chat_input("Por favor, deja tu número de WhatsApp (ejemplo: +5491123456789)")

# Procesar mensaje del usuario
if user_input:

    if st.session_state.awaiting_whatsapp:
        # Validate WhatsApp number
        if validate_whatsapp_number(user_input.strip()):
            # Send WhatsApp message to admin
            success = send_whatsapp_message(
                ADMIN_NUMBER,
                f"[Ayudín BOT]\nUsuario: {user_input.strip()}\nConsulta: \"{st.session_state.pending_question}\"\n(No pudo ser respondida automáticamente)"
            )
            if success:
                bot_message = "¡Gracias! Un compañero de Ayudín se contactará contigo a la brevedad por WhatsApp."
            else:
                bot_message = "Lo siento, hubo un error enviando tu consulta. Por favor, intenta más tarde o revisa el número."
            st.session_state.messages.append({"role": "bot", "content": bot_message})
            # Reset state
            st.session_state.awaiting_whatsapp = False
            st.session_state.pending_question = ""
            st.session_state.whatsapp_prompt_sent = False
        else:
            # Ask again
            st.session_state.messages.append({"role": "bot", "content": "El número ingresado no es válido. Por favor, usa el formato internacional: +5491123456789"})
    else:
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

        if ("desconozco sobre ese tema" in response or "dejas tu contacto" in response):
            st.session_state.awaiting_whatsapp = True
            st.session_state.pending_question = user_input
            st.session_state.whatsapp_prompt_sent = True
            st.session_state.messages.append({"role": "bot", "content": "Por favor, deja tu número de WhatsApp (ejemplo: +5491123456789) y derivaré tu consulta a un compañero."})
        # Forzar la re-ejecución para que la barra lateral se actualice inmediatamente
        st.rerun()

# Mostrar historial del chat con el método nativo de Streamlit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
