import streamlit as st
from groq import Groq

# =========================================
# CONFIGURACIÓN DE PROFESORES
# =========================================
PROFESORES = {
    "estadistica": {
        "nombre": "Profesor Ferrarre",
        "emoji": "📊",
        "estilo": "Práctico y numérico",
        "sistema_prompt": """Eres el Profesor Ferrarre, experto en estadística. 
Tu estilo es práctico, directo y motivador. 
Enfócate en ejercicios prácticos, procesos paso a paso y explicaciones numéricas.
Siempre da ejemplos concretos y consejos para aprobar la materia.
Responde en español de manera clara y útil."""
    },
    "desarrollo_ia": {
        "nombre": "Especialista IA", 
        "emoji": "🤖",
        "estilo": "Técnico y práctico", 
        "sistema_prompt": """Eres un Especialista en IA técnico y práctico.
Explica conceptos de manera clara, enfócate en fundamentos y proyectos reales.
Sé preciso, moderno y siempre da ejemplos de código cuando sea útil.
Responde en español de manera técnica pero accesible."""
    },
    "campo_laboral": {
        "nombre": "Profesora Acri",
        "emoji": "💼", 
        "estilo": "Exigente y profesional",
        "sistema_prompt": """Eres la Profesora Acri, exigente pero constructiva.
Enfócate en profesionalismo, preparación para entrevistas y desarrollo career.
Sé directa, orientada a resultados y da consejos prácticos para el mundo laboral.
Responde en español con un tono profesional y motivador."""
    },
    "comunicacion": {
        "nombre": "Especialista Comunicación",
        "emoji": "🎯",
        "estilo": "Claro y estructurado",
        "sistema_prompt": """Eres un Especialista en Comunicación claro y estructurado.
Enseña con ejemplos concretos, enfócate en estructura de mensajes y adaptación al público.
Sé amable, organizado y siempre da técnicas prácticas.
Responde en español de manera clara y ejemplificada."""
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias con Groq",
    page_icon="🎓",
    layout="wide"
)

# =========================================
# INICIALIZAR GROQ
# =========================================
try:
    client = Groq(api_key=st.secrets["groq_api_key"])
except Exception as e:
    st.error(f"❌ Error configurando Groq: {str(e)}")
    st.info("🔑 Configura GROQ_API_KEY en los secrets de Streamlit Cloud")
    st.stop()

# =========================================
# INTERFAZ PRINCIPAL
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias con Groq")
    st.markdown("### Potenciado por Llama 3.3 70B - Respuestas instantáneas 🚀")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Selecciona Materia")
        
        selected_materia = st.selectbox(
            "Elige tu materia:",
            list(PROFESORES.keys()),
            format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
        )
        
        profesor = PROFESORES[selected_materia]
        st.subheader(f"{profesor['emoji']} {profesor['nombre']}")
        st.write(f"**Estilo:** {profesor['estilo']}")
        
        st.markdown("---")
        st.subheader("⚙️ Configuración")
        
        modelo = st.selectbox(
            "Modelo Groq:",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0
        )
        
        temperature = st.slider("Creatividad:", 0.1, 1.0, 0.7, 0.1)
        
        st.markdown("---")
        if st.button("🧹 Limpiar Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Inicializar chat específico por materia
    chat_key = f"messages_{selected_materia}"
    if chat_key not in st.session_state:
        profesor = PROFESORES[selected_materia]
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"¡Hola! Soy {profesor['nombre']} {profesor['emoji']}. ¿En qué puedo ayudarte con {selected_materia.replace('_', ' ')}?"}
        ]
    
    # Mostrar historial de chat
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Procesar preguntas
    if prompt := st.chat_input(f"Pregunta sobre {selected_materia.replace('_', ' ')}..."):
        # Agregar mensaje del usuario
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner(f"💭 {PROFESORES[selected_materia]['nombre']} piensa..."):
                try:
                    profesor = PROFESORES[selected_materia]
                    
                    # Preparar mensajes con personalidad del profesor
                    messages = [
                        {"role": "system", "content": profesor['sistema_prompt']},
                        *st.session_state[chat_key]
                    ]
                    
                    # Llamar a Groq
                    response = client.chat.completions.create(
                        messages=messages,
                        model=modelo,
                        temperature=temperature,
                        max_tokens=1024,
                        stream=True
                    )
                    
                    # Mostrar con efecto de escritura
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                    # Agregar al historial
                    st.session_state[chat_key].append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
    
    # Footer informativo
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**{PROFESORES[selected_materia]['nombre']}** - {PROFESORES[selected_materia]['estilo']}")
    
    with col2:
        st.success("🚀 **Potenciado por Groq** - Modelos Llama 3.3 70B")

if __name__ == "__main__":
    main()
