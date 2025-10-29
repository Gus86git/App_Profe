import streamlit as st
import time
import os

# Configuración
st.set_page_config(
    page_title="Asistente 4 Materias + Búsqueda",
    page_icon="🎓",
    layout="wide"
)

# Título
st.title("🎓 Asistente 4 Materias + Búsqueda Semántica")
st.markdown("### Ahora con búsqueda inteligente en tu material")

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

# Cargar base de conocimiento con búsqueda semántica
@st.cache_resource
def cargar_busqueda_semantica():
    """Cargar sistema de búsqueda semántica"""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document

        # Verificar carpeta conocimiento
        if not os.path.exists("conocimiento"):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None

        # Cargar embeddings (esto funciona sin torch pesado)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Cargar documentos
        documentos = []
        for materia_dir in os.listdir("conocimiento"):
            materia_path = os.path.join("conocimiento", materia_dir)
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
                                        metadata={"materia": materia_dir, "archivo": archivo}
                                    )
                                )
                        except Exception as e:
                            continue

        if not documentos:
            st.error("❌ No se encontraron documentos")
            return None

        # Procesar documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )
        documentos_divididos = text_splitter.split_documents(documentos)

        # Crear vectorstore
        vectorstore = FAISS.from_documents(documentos_divididos, embeddings)
        st.success(f"✅ Búsqueda semántica activada: {len(documentos)} documentos indexados")
        return vectorstore

    except Exception as e:
        st.error(f"❌ Error en búsqueda semántica: {e}")
        return None

# Cargar sistema de búsqueda
with st.spinner("🔄 Activando búsqueda inteligente..."):
    buscador = cargar_busqueda_semantica()

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy tu asistente para {materia['nombre']}. Ahora puedo buscar en todo tu material. 🎓"}
    ]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función de búsqueda mejorada
def buscar_respuesta_inteligente(pregunta, materia):
    """Buscar respuesta en el material con contexto específico"""
    if buscador is None:
        return "Sistema de búsqueda no disponible", []
    
    try:
        # Buscar documentos relevantes
        documentos = buscador.similarity_search(pregunta, k=3)
        
        # Filtrar por materia si hay coincidencias
        docs_materia = [doc for doc in documentos if doc.metadata.get("materia") == materia]
        
        # Usar todos si no hay de la materia específica
        documentos_usar = docs_materia if docs_materia else documentos
        
        if not documentos_usar:
            return "No encontré información específica para tu pregunta en el material disponible.", []
        
        # Construir respuesta contextual
        contexto = "\n\n".join([doc.page_content for doc in documentos_usar])
        
        # Generar respuesta basada en el contexto
        respuesta_base = f"""
**🔍 Encontré esta información relevante en el material de {MATERIAS[materia]['nombre']}:**

{contexto}

**💡 Mi análisis:**
Basándome en el material, puedo ver que esta información es relevante para tu pregunta sobre "{pregunta}".

**🎯 Consejo práctico:**
{MATERIAS[materia]['consejo']}
"""
        
        return respuesta_base, documentos_usar
        
    except Exception as e:
        return f"Error en búsqueda: {str(e)}", []

# Input del usuario
if prompt := st.chat_input(f"Pregunta sobre {materia['nombre']}..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Buscar y generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando en el material..."):
            respuesta, documentos_encontrados = buscar_respuesta_inteligente(prompt, materia_seleccionada)
            
            # Efecto de escritura
            placeholder = st.empty()
            respuesta_completa = ""
            
            for chunk in respuesta.split():
                respuesta_completa += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(respuesta_completa + "▌")
            
            placeholder.markdown(respuesta_completa)
            
            # Mostrar fuentes si hay documentos encontrados
            if documentos_encontrados:
                with st.expander("📁 Ver fuentes encontradas"):
                    for i, doc in enumerate(documentos_encontrados):
                        st.write(f"**Fuente {i+1}:** {doc.metadata.get('archivo', 'Desconocido')}")
                        st.write(f"*Materia:* {doc.metadata.get('materia', 'General')}")
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})

# Información del estado
st.markdown("---")
st.success("""
**🎉 ¡Búsqueda Semántica Activada!**

**✅ Nuevas Capacidades:**
- 🔍 Búsqueda inteligente en TODO tu material
- 📚 Indexación automática de documentos
- 🎯 Respuestas contextuales específicas
- 📁 Visualización de fuentes encontradas

**🚀 Próximo Paso: IA Generativa**
- Una vez confirmado que la búsqueda funciona
- Agregaremos el modelo de lenguaje para respuestas más naturales
- Mantendremos la búsqueda semántica como base

**💡 Cómo probar:**
- Pregunta sobre temas específicos de tus materias
- Usa palabras clave de tus archivos
- Verifica que encuentre información relevante
""")

st.markdown("---")
st.markdown("🎓 **Asistente 4 Materias + Búsqueda Semántica** • Streamlit Cloud")
