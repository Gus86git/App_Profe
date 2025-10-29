import os
import streamlit as st
from groq import Groq

# Configuración de la página
st.set_page_config(
    page_title="Asistente IA con Groq",
    page_icon="🤖", 
    layout="wide"
)

# Título principal
st.title("💬 Asistente IA con Groq")
st.markdown("### Potenciado por Llama 3.3 70B - Ultra rápido 🚀")

# Inicializar cliente Groq
try:
    # En Streamlit Cloud usa st.secrets, localmente usa .env
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
    
    client = Groq(api_key=api_key)
    st.success("✅ Groq client configurado correctamente")
    
except Exception as e:
    st.error(f"❌ Error configurando Groq: {str(e)}")
    st.info("💡 Asegúrate de configurar GROQ_API_KEY en los secrets de Streamlit Cloud")
    st.stop()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712039.png", width=100)
    st.title("Configuración 🤖")
    
    # Selector de modelo
    modelo = st.selectbox(
        "Modelo:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0
    )
    
    memory_enabled = st.toggle("Activar memoria de chat", value=True)
    
    st.markdown("---")
    if st.button("🧹 Limpiar Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente IA potenciado por Groq. ¿En qué puedo ayudarte hoy? 🚀"}
    ]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🤖 Generando respuesta..."):
            try:
                # Preparar mensajes para la API
                if memory_enabled:
                    messages = [
                        {"role": "system", "content": "Eres un asistente IA útil y amigable. Responde en español."},
                        *st.session_state.messages
                    ]
                else:
                    messages = [
                        {"role": "system", "content": "Eres un asistente IA útil y amigable. Responde en español."},
                        {"role": "user", "content": prompt}
                    ]
                
                # Llamar a Groq
                response = client.chat.completions.create(
                    messages=messages,
                    model=modelo,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                bot_reply = response.choices[0].message.content
                
                # Mostrar respuesta con efecto de escritura
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in bot_reply.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Agregar al historial
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.success("🚀 **Asistente funcionando con Groq API** - Modelos Llama 3.3 70B - Ultra rápido")
