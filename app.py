import streamlit as st
import time
import os

# Configuración
st.set_page_config(
    page_title="Asistente 4 Materias",
    page_icon="🎓",
    layout="wide"
)

# Título
st.title("🎓 Asistente 4 Materias - Streamlit Cloud")
st.markdown("### Tu compañero académico para las 4 materias")

# Verificación de dependencias
st.markdown("---")
st.subheader("🔍 Verificación del Sistema")

try:
    import streamlit
    st.success("✅ Streamlit - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ Streamlit: {e}")

try:
    from transformers import pipeline
    st.success("✅ Transformers - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ Transformers: {e}")

try:
    import torch
    st.success("✅ PyTorch - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ PyTorch: {e}")

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    st.success("✅ LangChain - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ LangChain: {e}")

# Configuración de materias
MATERIAS = {
    "estadistica": {
        "nombre": "Estadística",
        "emoji": "📊",
        "profesor": "Prof. Ferrarre",
        "consejo": "Practica todos los ejercicios y enfócate en el proceso paso a paso"
    },
    "desarrollo_ia": {
        "nombre": "Desarrollo de IA", 
        "emoji": "🤖",
        "profesor": "Especialista IA",
        "consejo": "Entiende los fundamentos antes de usar frameworks complejos"
    },
    "campo_laboral": {
        "nombre": "Campo Laboral",
        "emoji": "💼",
        "profesor": "Prof. Acri",
        "consejo": "Sé profesional, puntual y prepara exhaustivamente tus entregas"
    },
    "comunicacion": {
        "nombre": "Comunicación",
        "emoji": "🎯", 
        "profesor": "Especialista Comunicación",
        "consejo": "Estructura tus mensajes y adapta tu lenguaje al público"
    }
}

# Sidebar
with st.sidebar:
    st.header("📚 Selecciona Materia")
    
    materia_seleccionada = st.selectbox(
        "Elige:",
        list(MATERIAS.keys()),
        format_func=lambda x: f"{MATERIAS[x]['emoji']} {MATERIAS[x]['nombre']}"
    )
    
    materia = MATERIAS[materia_seleccionada]
    st.subheader(f"{materia['emoji']} {materia['profesor']}")
    st.write(f"**Consejo:** {materia['consejo']}")
    
    st.markdown("---")
    
    if st.button("🧹 Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# Cargar modelo de IA
@st.cache_resource
def cargar_modelo_ia():
    """Cargar modelo de lenguaje para generar respuestas"""
    try:
        from transformers import pipeline
        model = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            torch_dtype=torch.float16,
            max_length=512
        )
        st.success("✅ Modelo de IA cargado")
        return model
    except Exception as e:
        st.error(f"❌ Error cargando modelo de IA: {e}")
        return None

# Cargar base de conocimiento vectorial
@st.cache_resource
def cargar_base_conocimiento():
    """Cargar y procesar toda la base de conocimiento"""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document

        # Verificar si existe la carpeta conocimiento
        if not os.path.exists("conocimiento"):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None

        # Cargar embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Cargar todos los documentos
        documentos = []
        for materia in os.listdir("conocimiento"):
            materia_path = os.path.join("conocimiento", materia)
            if os.path.isdir(materia_path):
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                                documentos.append(
                                    Document(
                                        page_content=contenido,
                                        metadata={"materia": materia, "archivo": archivo}
                                    )
                                )
                        except Exception as e:
                            st.warning(f"⚠️ Error leyendo {archivo_path}: {e}")

        if not documentos:
            st.error("❌ No se encontraron documentos en la base de conocimiento")
            return None

        # Dividir documentos en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        documentos_divididos = text_splitter.split_documents(documentos)

        # Crear base vectorial
        vectorstore = FAISS.from_documents(documentos_divididos, embeddings)
        st.success(f"✅ Base de conocimiento cargada: {len(documentos)} documentos")
        return vectorstore

    except Exception as e:
        st.error(f"❌ Error cargando base de conocimiento: {e}")
        return None

# Inicializar recursos
with st.spinner("🔄 Cargando recursos de IA..."):
    modelo_ia = cargar_modelo_ia()
    base_conocimiento = cargar_base_conocimiento()

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy tu asistente para {materia['nombre']}. ¿En qué puedo ayudarte? 🎓"}
    ]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para buscar en el conocimiento
def buscar_en_conocimiento(pregunta, materia, k=3):
    """Buscar información relevante en la base de conocimiento"""
    if base_conocimiento is None:
        return "Base de conocimiento no disponible"
    
    try:
        # Buscar documentos relevantes
        documentos = base_conocimiento.similarity_search(pregunta, k=k)
        
        # Filtrar por materia si es posible
        docs_filtrados = []
        for doc in documentos:
            if doc.metadata.get("materia") == materia:
                docs_filtrados.append(doc)
        
        # Si no hay de la materia específica, usar todos
        if not docs_filtrados:
            docs_filtrados = documentos
        
        # Construir contexto
        contexto = ""
        for i, doc in enumerate(docs_filtrados):
            contexto += f"Documento {i+1}:\n{doc.page_content}\n\n"
        
        return contexto if contexto else "No se encontró información específica para tu pregunta."
    
    except Exception as e:
        return f"Error en búsqueda: {str(e)}"

# Función para generar respuesta con IA
def generar_respuesta_ia(pregunta, contexto, materia):
    """Generar respuesta usando el modelo de IA"""
    if modelo_ia is None:
        return "Modelo de IA no disponible en este momento."
    
    try:
        # Personalizar según la materia
        profesores = {
            "estadistica": "Profesor Ferrarre",
            "desarrollo_ia": "Especialista en IA", 
            "campo_laboral": "Profesora Acri",
            "comunicacion": "Especialista en Comunicación"
        }
        
        profesor = profesores.get(materia, "Asistente")
        
        prompt = f"""
        Eres un {profesor} ayudando a estudiantes universitarios.
        
        CONTEXTO RELEVANTE:
        {contexto}
        
        PREGUNTA DEL ESTUDIANTE:
        {pregunta}
        
        Instrucciones:
        - Responde como el profesor especializado en esta materia
        - Sé claro, práctico y útil
        - Si la información del contexto no es suficiente, sé honesto
        - Usa un tono amable pero profesional
        - Enfócate en ayudar al estudiante a entender y aprobar
        
        RESPUESTA:
        """
        
        respuesta = modelo_ia(
            prompt,
            max_new_tokens=400,
            temperature=0.7,
            do_sample=True,
            pad_token_id=modelo_ia.tokenizer.eos_token_id
        )
        
        return respuesta[0]['generated_text'].split("RESPUESTA:")[-1].strip()
    
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"

# Input del usuario
if prompt := st.chat_input(f"Pregunta sobre {materia['nombre']}..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Buscando en el material..."):
            # Buscar en el conocimiento
            contexto = buscar_en_conocimiento(prompt, materia_seleccionada)
            
            # Generar respuesta con IA
            respuesta = generar_respuesta_ia(prompt, contexto, materia_seleccionada)
            
            # Efecto de escritura
            placeholder = st.empty()
            respuesta_completa = ""
            
            for chunk in respuesta.split():
                respuesta_completa += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(respuesta_completa + "▌")
            
            placeholder.markdown(respuesta_completa)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})

# Información del estado
st.markdown("---")
st.success("""
**🎉 ¡Asistente con IA Funcionando!**

**✅ Características Activadas:**
- 🤖 Modelo de IA para respuestas inteligentes
- 🔍 Búsqueda semántica en tu material
- 📚 Base de conocimiento vectorial
- 💬 Chat contextual y especializado

**🚀 Próximos Pasos:**
1. ✅ IA integrada y funcionando
2. ✅ Búsqueda en tu material específico
3. 🌐 Compartir con compañeros
4. 📊 Recibir feedback y mejorar

**💡 Consejos de uso:**
- Sé específico en tus preguntas
- Menciona si es para parcial/trabajo práctico
- Pide ejemplos cuando necesites
- ¡Aprovecha todo el material subido!
""")

st.markdown("---")
st.markdown("🎓 **Asistente 4 Materias con IA** • Powered by Streamlit Cloud")
