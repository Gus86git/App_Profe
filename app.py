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
        "consejos": [
            "Practica TODOS los ejercicios de las guías",
            "Enfócate en entender el proceso, no solo el resultado",
            "Los parciales suelen ser similares a los ejercicios de clase",
            "No te saltes pasos en los desarrollos",
            "Revisa bien las unidades de medida y decimales"
        ]
    },
    "desarrollo_ia": {
        "nombre": "Especialista IA", 
        "emoji": "🤖",
        "estilo": "Técnico y práctico",
        "consejos": [
            "Empieza con los fundamentos antes de frameworks",
            "Practica con proyectos pequeños primero",
            "Documenta bien tu código",
            "Revisa los algoritmos base antes de implementaciones complejas",
            "Testea cada componente por separado"
        ]
    },
    "campo_laboral": {
        "nombre": "Profesora Acri",
        "emoji": "💼", 
        "estilo": "Exigente y profesional",
        "consejos": [
            "Sé impecable en presentaciones y entregas",
            "Investiga la empresa antes de entrevistas",
            "Prepara preguntas inteligentes para los reclutadores",
            "Tu CV debe ser claro y sin errores",
            "Practica tu pitch personal múltiples veces"
        ]
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
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias + Conocimiento",
    page_icon="🎓",
    layout="wide"
)

# =========================================
# FUNCIÓN PARA CARGAR CONOCIMIENTO
# =========================================
def cargar_conocimiento():
    """Cargar todo el conocimiento desde archivos .txt"""
    conocimiento = {}
    
    try:
        base_path = "conocimiento"
        if not os.path.exists(base_path):
            st.warning("📁 No se encuentra la carpeta 'conocimiento'")
            return conocimiento
        
        for materia in os.listdir(base_path):
            materia_path = os.path.join(base_path, materia)
            if os.path.isdir(materia_path):
                conocimiento[materia] = ""
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                                conocimiento[materia] += f"\n--- {archivo} ---\n{contenido}\n"
                        except Exception as e:
                            st.warning(f"⚠️ Error leyendo {archivo}: {str(e)}")
        
        return conocimiento
    except Exception as e:
        st.error(f"❌ Error cargando conocimiento: {str(e)}")
        return {}

# =========================================
# FUNCIÓN MEJORADA DE RESPUESTAS
# =========================================
def generar_respuesta_mejorada(pregunta, materia, conocimiento):
    """Generar respuesta usando el conocimiento cargado"""
    profesor = PROFESORES[materia]
    
    # Buscar términos relevantes en el conocimiento
    contexto = ""
    if materia in conocimiento:
        contenido_materia = conocimiento[materia].lower()
        palabras_pregunta = pregunta.lower().split()
        
        # Buscar palabras clave de la pregunta en el conocimiento
        for palabra in palabras_pregunta:
            if len(palabra) > 4 and palabra in contenido_materia:
                # Encontrar el párrafo donde aparece la palabra
                lineas = conocimiento[materia].split('\n')
                for linea in lineas:
                    if palabra in linea.lower():
                        contexto = linea[:200] + "..."
                        break
                if contexto:
                    break
    
    # Respuestas base mejoradas
    respuestas_mejoradas = {
        "estadistica": [
            f"📊 **{profesor['nombre']} responde:** {random.choice(profesor['consejos'])}",
            f"📊 **Sobre '{pregunta}':** En estadística, {random.choice(profesor['consejos'])}",
            f"📊 **{profesor['nombre']} aconseja:** {random.choice(profesor['consejos'])}"
        ],
        "desarrollo_ia": [
            f"🤖 **{profesor['nombre']} explica:** {random.choice(profesor['consejos'])}", 
            f"🤖 **Para '{pregunta}':** En desarrollo de IA, {random.choice(profesor['consejos'])}",
            f"🤖 **{profesor['nombre']} recomienda:** {random.choice(profesor['consejos'])}"
        ],
        "campo_laboral": [
            f"💼 **{profesor['nombre']} enfatiza:** {random.choice(profesor['consejos'])}",
            f"💼 **Sobre '{pregunta}':** En el campo laboral, {random.choice(profesor['consejos'])}",
            f"💼 **{profesor['nombre']} destaca:** {random.choice(profesor['consejos'])}"
        ],
        "comunicacion": [
            f"🎯 **{profesor['nombre']} sugiere:** {random.choice(profesor['consejos'])}",
            f"🎯 **Para '{pregunta}':** En comunicación, {random.choice(profesor['consejos'])}", 
            f"🎯 **{profesor['nombre']} recomienda:** {random.choice(profesor['consejos'])}"
        ]
    }
    
    respuesta_base = random.choice(respuestas_mejoradas[materia])
    
    # Construir respuesta final
    respuesta_final = f"""
    {respuesta_base}
    
    **💡 Estilo {profesor['nombre']}:** {profesor['estilo']}
    """
    
    # Añadir contexto si se encontró información relevante
    if contexto:
        respuesta_final += f"""
        
    **📚 Encontré en el material:**
    *"{contexto}"*
        """
    
    # Añadir consejo adicional
    respuesta_final += f"""
    
    **🎯 Recuerda siempre:** {random.choice(profesor['consejos'])}
    """
    
    return respuesta_final

# =========================================
# INTERFAZ PRINCIPAL MEJORADA
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias + Conocimiento")
    st.markdown("### Ahora con acceso a todo tu material de estudio")
    
    # Cargar conocimiento al inicio
    with st.spinner("📚 Cargando material de estudio..."):
        conocimiento = cargar_conocimiento()
    
    # Sidebar mejorado
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
        
        st.markdown("**Consejos clave:**")
        for consejo in profesor['consejos'][:3]:
            st.write(f"• {consejo}")
        
        # Mostrar estado del conocimiento
        st.markdown("---")
        st.subheader("📂 Estado del Conocimiento")
        
        if conocimiento:
            materias_cargadas = [m for m in conocimiento if conocimiento[m]]
            st.success(f"✅ {len(materias_cargadas)} materias cargadas")
            
            for materia in PROFESORES.keys():
                if materia in conocimiento and conocimiento[materia]:
                    archivos = conocimiento[materia].count('---') // 2
                    st.write(f"• {PROFESORES[materia]['emoji']} {materia}: {archivos} archivos")
        else:
            st.warning("⚠️ Sin conocimiento cargado")
        
        st.markdown("---")
        
        if st.button("🧹 Limpiar Conversación", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"¡Hola! Soy {PROFESORES[selected_materia]['nombre']} {PROFESORES[selected_materia]['emoji']}. Ahora puedo acceder a tu material de estudio. ¿En qué puedo ayudarte?"}
        ]
    
    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input(f"Pregunta sobre {selected_materia.replace('_', ' ')}..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner(f"💭 {PROFESORES[selected_materia]['nombre']} busca en el material..."):
                respuesta = generar_respuesta_mejorada(prompt, selected_materia, conocimiento)
                
                # Efecto de escritura
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in respuesta.split():
                    full_response += chunk + " "
                    time.sleep(0.03)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Footer informativo
    st.markdown("---")
    st.success("""
    **🚀 ¡Nueva funcionalidad agregada!**
    
    **✅ Ahora con:**
    - Carga automática de archivos .txt
    - Búsqueda básica en tu material
    - Respuestas contextuales mejoradas
    - Estado del conocimiento en tiempo real
    
    **📈 Próximo paso:** Agregar búsqueda semántica inteligente
    """)

if __name__ == "__main__":
    main()

