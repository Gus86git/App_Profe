# app.py

import streamlit as st
import os
import time
import random

# =========================================
# CONFIGURACIÓN DE PROFESORES
# =========================================
PROFESORES = {
    "estadistica": {
        "nombre": "Profesor Ferrarre",
        "emoji": "📊",
        "estilo": "Práctico y numérico",
        "consejos":
    },
    "desarrollo_ia": {
        "nombre": "Especialista IA", 
        "emoji": "🤖",
        "estilo": "Técnico y práctico",
        "consejos":
    },
    "campo_laboral": {
        "nombre": "Profesora Acri",
        "emoji": "💼", 
        "estilo": "Exigente y profesional",
        "consejos":
    },
    "comunicacion": {
        "nombre": "Especialista Comunicación",
        "emoji": "🎯",
        "estilo": "Claro y estructurado", 
        "consejos": [
            "Estructura tu mensaje antes de hablar",
            "Practica la escucha activa",
            "Adapta tu lenguaje al público",
            "Usa ejemplos concretos en tus explicaciones",
            "Maneja bien los tiempos en presentaciones"
        ]
    }}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias - Streamlit Cloud",
    page_icon="🎓",
    layout="wide")

# =========================================
# FUNCIONES PRINCIPALES (CARGA DE TEXTO)
# =========================================

@st.cache_resource(show_spinner=False)
def cargar_conocimiento():
    """Carga todo el conocimiento de los archivos de texto en un diccionario."""
    conocimiento = {}
    try:
        base_path = "conocimiento"
        if not os.path.exists(base_path):
            return conocimiento
            
        for materia in os.listdir(base_path):
            materia_path = os.path.join(base_path, materia)
            if os.path.isdir(materia_path):
                # Guarda todo el texto de la materia en una sola entrada
                contenido_materia = ""
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                # Etiqueta el contenido con el nombre del archivo (para simular citación)
                                contenido_materia += f"\n--- Archivo: {archivo} ---\n{f.read()}\n"
                        except Exception as e:
                            st.warning(f"⚠️ Error leyendo {archivo_path}")
                conocimiento[materia] = contenido_materia
        return conocimiento
    except Exception as e:
        st.error(f"❌ Error cargando conocimiento: {e}")
        return {}

def generar_respuesta_profesor(pregunta, materia, conocimiento):
    """Genera respuesta simulada con contexto y personalidad."""
    profesor = PROFESORES[materia]
    
    # 1. Recuperación simulada de contexto
    contexto_completo = conocimiento.get(materia, "")
    
    # Intenta encontrar un snippet de contexto (simula RAG)
    contexto_relevante = ""
    if contexto_completo:
        # Usaremos la primera parte del texto como contexto simulado
        contexto_lines = contexto_completo.split('\n')
        # Buscamos un fragmento de 500 caracteres
        contexto_relevante = contexto_completo[:500] 

    # 2. Generación de respuesta (simulada)
    respuesta_base = f"""
    {profesor['emoji']} **¡Atención! {profesor['nombre']} (Estilo {profesor['estilo']}):**

    Para tu consulta sobre **'{pregunta}'**, recuerda que el enfoque en **{materia.replace('_', ' ').title()}** es clave.
    
    En este momento, te recomiendo concentrarte en: {random.choice(profesor['consejos'])}.
    
    """
    
    # 3. Adición de citación simulada
    if contexto_relevante:
        respuesta_base += f"""
        
        --—
        
        **📚 Referencia RAG (Simulada):**
        
        He encontrado este fragmento en tus materiales de **{materia.replace('_', ' ').title()}** que puede serte útil:
        
        *...{contexto_relevante.strip().replace('--- Archivo:', '\n
        )
        
        profesor = PROFESORES[selected_materia]
        st.subheader(f"{profesor['emoji']} {profesor['nombre']}")
        st.write(f"**Estilo:** {profesor['estilo']}")
        
        st.markdown("**Consejos clave:**")
        for consejo in profesor['consejos'][:3]:
            st.write(f"• {consejo}")
        
        st.markdown("---")
        
        st.subheader("🔍 Estado del Sistema")
        st.success("✅ Streamlit (Única dependencia)")
        st.success("✅ RAG (Recuperación) Simulada por Texto")
        st.success("✅ 100% Gratis y Sin Claves API")
        
        st.markdown("---")
        
        if st.button("🧹 Limpiar Conversación", use_container_width=True):
            if "messages" in st.session_state:
                st.session_state.messages =
            st.rerun()
    
    # 2. Cargar conocimiento (la parte más lenta)
    with st.spinner("📚 Cargando material de estudio (solo texto)..."):
        conocimiento = cargar_conocimiento()
        
    # 3. Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages =}. La base de conocimiento está cargada. ¿En qué puedo ayudarte con {selected_materia.replace('_', ' ').title()}? 🎓"}
        ]
    
    # 4. Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 5. Input del usuario
    if prompt := st.chat_input(f"Escribe tu pregunta sobre {selected_materia.replace('_', ' ')}..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner(f"💭 {profesor['nombre']} está revisando los materiales..."):
                respuesta = generar_respuesta_profesor(prompt, selected_materia, conocimiento)
                
                # Efecto de escritura
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in respuesta.split():
                    full_response += chunk + " "
                    time.sleep(0.01) # Velocidad aumentada para Streamlit Cloud
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Footer informativo
    st.markdown("---")
    st.info("""
    **🚀 NOTA IMPORTANTE:** Esta versión fue optimizada para evitar errores de memoria/instalación en el Plan Gratuito de Streamlit Cloud. Se eliminó la IA pesada (`torch`, `faiss`) y se utiliza la recuperación de texto pura, manteniendo el filtro por materia y la simulación de citación.
    """)

# =========================================
# EJECUCIÓN PRINCIPAL
# =========================================
if __name__ == "__main__":
    main()
