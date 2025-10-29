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
        ],
        "respuestas": [
            "En estadística, la práctica constante es clave. Resuelve todos los ejercicios de las guías.",
            "Recuerda: entender el proceso es más importante que el resultado final.",
            "Los números no mienten, pero hay que saber interpretarlos correctamente."
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
        ],
        "respuestas": [
            "En IA, domina los fundamentos antes de pasar a frameworks avanzados.",
            "La práctica con proyectos pequeños te dará una base sólida.",
            "Documenta cada parte de tu código para futuras referencias."
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
        ],
        "respuestas": [
            "La profesionalidad se demuestra en los detalles. Sé impecable en todo.",
            "Investiga exhaustivamente cada empresa antes de las entrevistas.",
            "Tu CV es tu primera impresión - debe ser perfecto."
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
        ],
        "respuestas": [
            "La comunicación efectiva comienza con una estructura clara.",
            "Adapta tu mensaje al público para mayor impacto.",
            "Practica la escucha tanto como el habla."
        ]
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias",
    page_icon="🎓",
    layout="wide"
)

def main():
    st.title("🎓 Asistente 4 Materias")
    st.markdown("### Tu compañero académico - Versión Estable")
    
    # Sidebar simple
    with st.sidebar:
        st.header("📚 Materias")
        
        materia = st.selectbox(
            "Selecciona:",
            list(PROFESORES.keys()),
            format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
        )
        
        profe = PROFESORES[materia]
        st.write(f"**Estilo:** {profe['estilo']}")
        
        st.markdown("**Consejos:**")
        for consejo in profe['consejos'][:2]:
            st.write(f"• {consejo}")
        
        st.markdown("---")
        
        if st.button("🧹 Limpiar Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"¡Hola! Soy {PROFESORES[materia]['nombre']} {PROFESORES[materia]['emoji']}. ¿En qué puedo ayudarte?"}
        ]
    
    # Mostrar chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Función de respuesta simple
    def responder_pregunta(pregunta, materia):
        profe = PROFESORES[materia]
        respuesta_base = random.choice(profe['respuestas'])
        
        return f"""
        {profe['emoji']} **{profe['nombre']} dice:**
        
        {respuesta_base}
        
        **Sobre tu pregunta:** "{pregunta}"
        
        💡 *Consejo práctico:* {random.choice(profe['consejos'])}
        
        🎯 *Recuerda:* {profe['estilo']}
        """
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = responder_pregunta(prompt, materia)
                
                placeholder = st.empty()
                texto_completo = ""
                
                for palabra in respuesta.split():
                    texto_completo += palabra + " "
                    time.sleep(0.05)
                    placeholder.markdown(texto_completo + "▌")
                
                placeholder.markdown(texto_completo)
        
        st.session_state.messages.append({"role": "assistant", "content": texto_completo})
    
    # Footer
    st.markdown("---")
    st.success("✅ **Asistente funcionando correctamente en Streamlit Cloud**")

if __name__ == "__main__":
    main()
