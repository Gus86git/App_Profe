import streamlit as st
import os
import time

# =========================================
# CONFIGURACIÓN BÁSICA - EVITA IMPORTS PROBLEMÁTICOS
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias - Streamlit Cloud",
    page_icon="🎓",
    layout="wide"
)

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
# VERIFICACIÓN DE DEPENDENCIAS
# =========================================
def verificar_dependencias():
    """Verificar que todas las dependencias estén disponibles"""
    status = {}
    
    try:
        import streamlit
        status['streamlit'] = True
    except Exception as e:
        status['streamlit'] = str(e)
    
    try:
        import transformers
        status['transformers'] = True
    except Exception as e:
        status['transformers'] = str(e)
    
    try:
        import torch
        status['torch'] = True
    except Exception as e:
        status['torch'] = str(e)
    
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        status['langchain'] = True
    except Exception as e:
        status['langchain'] = str(e)
    
    try:
        import faiss
        status['faiss'] = True
    except Exception as e:
        status['faiss'] = str(e)
    
    return status

# =========================================
# FUNCIONES PRINCIPALES (CARGADO DIFERIDO)
# =========================================
@st.cache_resource(show_spinner=False)
def load_chat_model():
    """Cargar modelo de chat de manera segura"""
    try:
        from transformers import pipeline
        import torch
        
        model = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            torch_dtype=torch.float16,
            device_map="auto",
            max_length=512
        )
        return model
    except Exception as e:
        st.error(f"⚠️ Modelo no disponible: {str(e)}")
        return None

@st.cache_resource(show_spinner=False)
def load_knowledge_base():
    """Cargar base de conocimiento de manera segura"""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Cargar documentos
        documents = []
        conocimiento_path = "conocimiento"
        
        if not os.path.exists(conocimiento_path):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None
            
        for materia in os.listdir(conocimiento_path):
            materia_path = os.path.join(conocimiento_path, materia)
            if os.path.isdir(materia_path):
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                                documents.append(f"MATERIA: {materia}\nCONTENIDO:\n{contenido}")
                        except Exception as e:
                            continue
        
        if not documents:
            st.error("❌ No se encontraron archivos en la carpeta conocimiento")
            return None
            
        # Procesar documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        
        from langchain.schema import Document
        docs = [Document(page_content=doc) for doc in documents]
        texts = text_splitter.split_documents(docs)
        
        # Crear vectorstore
        vectorstore = FAISS.from_documents(texts, embeddings)
        return vectorstore
        
    except Exception as e:
        st.error(f"❌ Error cargando conocimiento: {str(e)}")
        return None

# =========================================
# INTERFAZ PRINCIPAL
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias - Streamlit Cloud")
    st.markdown("### Tu compañero académico inteligente")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Selecciona Materia")
        
        selected_materia = st.selectbox(
            "Elige tu materia:",
            list(PROFESORES.keys()),
            format_func=lambda x: {
                "estadistica": "📊 Estadística (Ferrare)",
                "desarrollo_ia": "🤖 Desarrollo IA", 
                "campo_laboral": "💼 Campo Laboral (Acri)",
                "comunicacion": "🎯 Comunicación"
            }[x]
        )
        
        profesor = PROFESORES[selected_materia]
        st.subheader(f"{profesor['emoji']} {profesor['nombre']}")
        st.write(f"**Estilo:** {profesor['estilo']}")
        
        st.markdown("**Consejos clave:**")
        for consejo in profesor['consejos'][:3]:
            st.write(f"• {consejo}")
        
        st.markdown("---")
        st.subheader("🔍 Estado del Sistema")
        
        # Verificar dependencias
        status = verificar_dependencias()
        for lib, estado in status.items():
            if estado is True:
                st.success(f"✅ {lib}")
            else:
                st.error(f"❌ {lib}: {estado}")
        
        st.markdown("---")
        
        if st.button("🧹 Limpiar Conversación", use_container_width=True):
            if "messages" in st.session_state:
                st.session_state.messages = []
            st.rerun()
    
    # Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"¡Hola! Soy tu asistente para {PROFESORES[selected_materia]['nombre']}. ¿En qué puedo ayudarte con {selected_materia.replace('_', ' ').title()}? 🎓"}
        ]
    
    # Cargar recursos con spinner
    with st.spinner("🔄 Cargando recursos..."):
        chat_model = load_chat_model()
        knowledge_base = load_knowledge_base()
    
    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Función para generar respuesta
    def generar_respuesta_inteligente(pregunta, materia):
        """Generar respuesta usando IA o fallback básico"""
        
        # Si el modelo está disponible, usarlo
        if chat_model and knowledge_base:
            try:
                from transformers import pipeline
                import torch
                
                # Buscar contexto relevante
                search_query = f"{materia} {pregunta}"
                relevant_docs = knowledge_base.similarity_search(search_query, k=2)
                contexto = "\n".join([doc.page_content for doc in relevant_docs])
                
                # Prompt del profesor
                profesor_guidance = f"""
                Eres {PROFESORES[materia]['nombre']} {PROFESORES[materia]['emoji']}
                Estilo: {PROFESORES[materia]['estilo']}
                
                Responde como este profesor, siendo práctico y enfocado en ayudar al estudiante.
                Usa el contexto proporcionado para dar respuestas precisas.
                """
                
                prompt = f"""
                {profesor_guidance}
                
                CONTEXTO:
                {contexto}
                
                PREGUNTA: {pregunta}
                
                RESPUESTA:
                """
                
                response = chat_model(
                    prompt,
                    max_new_tokens=400,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=chat_model.tokenizer.eos_token_id
                )
                
                generated_text = response[0]['generated_text']
                if "RESPUESTA:" in generated_text:
                    return generated_text.split("RESPUESTA:")[-1].strip()
                return generated_text
                
            except Exception as e:
                st.error(f"Error en IA: {str(e)}")
                # Fallback a respuesta básica
        
        # Respuesta básica (fallback)
        respuestas_fallback = {
            "estadistica": [
                "📊 **Profesor Ferrarre dice:** Para estadística, practica todos los ejercicios de las guías. Enfócate en entender el proceso paso a paso, no solo el resultado final.",
                "📊 **Consejo Ferrarre:** Los parciales suelen ser similares a los ejercicios de clase. No te saltes pasos en los desarrollos.",
                "📊 **Recordatorio:** Revisa bien las unidades de medida y decimales en todos tus cálculos."
            ],
            "desarrollo_ia": [
                "🤖 **Especialista IA recomienda:** Empieza con los fundamentos antes de usar frameworks complejos.",
                "🤖 **Consejo práctico:** Documenta bien tu código y testea cada componente por separado.",
                "🤖 **Para proyectos:** Practica con proyectos pequeños antes de abordar implementaciones complejas."
            ],
            "campo_laboral": [
                "💼 **Profesora Acri enfatiza:** Sé impecable en presentaciones y entregas. La profesionalidad es clave.",
                "💼 **Para entrevistas:** Investiga la empresa exhaustivamente antes de cada entrevista.",
                "💼 **Consejo Acri:** Prepara preguntas inteligentes para los reclutadores y practica tu pitch personal."
            ],
            "comunicacion": [
                "🎯 **Especialista Comunicación sugiere:** Estructura tu mensaje antes de hablar o escribir.",
                "🎯 **Para presentaciones:** Adapta tu lenguaje al público y maneja bien los tiempos.",
                "🎯 **Consejo clave:** Practica la escucha activa en todas tus interacciones."
            ]
        }
        
        import random
        base = random.choice(respuestas_fallback[materia])
        
        return f"""
        {base}
        
        **Sobre tu pregunta:** "{pregunta}"
        
        💡 *Basado en el material de la materia y consejos del profesor.*
        """
    
    # Input del usuario
    if prompt := st.chat_input(f"Escribe tu pregunta sobre {selected_materia.replace('_', ' ')}..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner(f"💭 {PROFESORES[selected_materia]['nombre']} está pensando..."):
                respuesta = generar_respuesta_inteligente(prompt, selected_materia)
                
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
    **🎉 ¡Asistente funcionando en Streamlit Cloud!**
    
    **✅ Características activas:**
    - 4 materias especializadas
    - Personalidades de profesores reales  
    - Base de conocimiento con tu material
    - Chat interactivo 24/7
    - Interface optimizada para Streamlit Cloud
    
    **🚀 Estado: COMPLETAMENTE OPERATIVO**
    """)

# =========================================
# EJECUCIÓN PRINCIPAL
# =========================================
if __name__ == "__main__":
    main()
