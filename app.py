# app.py

import os
import re
import streamlit as st
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings # Embeddings gratuitos
from langchain.chains import RetrievalQA
from langchain.llms.fake import FakeListLLM # LLM Simulado y gratuito

# --- Constantes de Configuración ---
KNOWLEDGE_PATH = "conocimiento/"
CHROMA_PERSIST_DIR = "chroma_db"
# Modelo de embeddings local y gratuito
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" 

# --- LLM Simulado (Completamente gratuito y sin clave) ---
# Este LLM simulará la respuesta pero las CITACIONES serán REALES.
# Se usa para demostrar que la parte RAG (filtrado y citación) funciona sin costo.
def get_fake_llm():
    # Definimos una lista de respuestas que el modelo "dará" en secuencia.
    responses = * 5 
    
    return FakeListLLM(responses=responses)

def get_subjects():
    """Detecta dinámicamente las materias (subdirectorios) disponibles."""
    subjects =
    if os.path.exists(KNOWLEDGE_PATH):
        # Listar subdirectorios en 'conocimiento/'
        for item in os.listdir(KNOWLEDGE_PATH):
            item_path = os.path.join(KNOWLEDGE_PATH, item)
            if os.path.isdir(item_path):
                # Formato: 'estadistica' -> 'Estadistica'
                subjects.append(item.replace('_', ' ').title())
    return sorted(subjects)

def extract_subject_metadata(path: str) -> dict:
    """Función crítica para extraer el metadato 'subject' (materia) 
    del path para permitir el filtrado dinámico en ChromaDB."""
    
    # Busca el nombre del subdirectorio inmediatamente después de 'conocimiento/'
    match = re.search(r"conocimiento/([^/]+)/", path)
    if match:
        # El metadato debe coincidir con el nombre usado en el checkbox
        subject = match.group(1).replace('_', ' ').title()
        return {"source": path, "subject": subject}
    return {"source": path, "subject": "General"}

@st.cache_resource(show_spinner=False)
def get_vector_store():
    """Inicializa o carga la base de datos vectorial persistida y cacheada."""
    
    # USO DE EMBEDDINGS GRATUITOS Y LOCALES
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
        with st.spinner("Cargando base de conocimiento persistida..."):
            # Carga rápida: Carga el índice desde el disco (evita re-embedding)
            vector_store = Chroma(
                persist_directory=CHROMA_PERSIST_DIR, 
                embedding_function=embeddings
            )
            return vector_store
    else:
        # Ingestión completa: Se ejecuta solo en el primer uso (o si se borra chroma_db)
        with st.spinner("Indexando documentos por primera vez (puede tardar en Streamlit Cloud, ¡pero solo una vez!)..."):
            
            # Carga de documentos con mapeo de metadatos custom
            loader = DirectoryLoader(
                KNOWLEDGE_PATH,
                glob="**/*.txt", # Soporte para todos los TXT
                loader_cls=TextLoader,
                loader_kwargs={'autodetect_encoding': True},
                silent_errors=True
            )
            documents = loader.load()

            # Aplicar la función de extracción de metadatos
            for doc in documents:
                new_metadata = extract_subject_metadata(doc.metadata.get('source', ''))
                doc.metadata.update(new_metadata)

            # Chunking (división en fragmentos)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_documents(documents)

            # Creación y persistencia
            vector_store = Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                persist_directory=CHROMA_PERSIST_DIR
            )
            # Guarda en disco para futuras ejecuciones (CRÍTICO para Streamlit Cloud)
            vector_store.persist() 
            return vector_store

def create_metadata_filter(active_subjects: list) -> dict:
    """Crea el filtro de metadatos 'where' para ChromaDB."""
    if not active_subjects:
        return None
    
    filter_clauses = [{"subject": {"$eq": sub}} for sub in active_subjects]
    return {"$or": filter_clauses}


def get_rag_chain(vector_store, active_subjects: list):
    """Construye la cadena RAG con el LLM Simulado y el retriever filtrado."""
    
    # LLM GRATUITO: Usa el LLM Falso/Simulado
    llm = get_fake_llm()

    metadata_filter = create_metadata_filter(active_subjects)
    
    # Inicialización del retriever con el filtro dinámico
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5, "filter": metadata_filter}
    )

    # RetrievalQA: obtiene la respuesta y los documentos fuente (citaciones)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

def sidebar_config(subjects):
    """Configura la barra lateral para la selección de fuentes estilo NotebookLM."""
    st.sidebar.title("📚 Fuentes de Conocimiento")
    st.sidebar.markdown("Selecciona las materias que el chatbot debe usar para responder.")
    st.sidebar.caption("💡 Esta versión es 100% gratuita y sin claves. El texto es simulado, pero las **citaciones** son el resultado de la búsqueda RAG.")

    if 'active_subjects' not in st.session_state:
        # Por defecto, todas las materias están activas
        st.session_state['active_subjects'] = subjects

    active_subjects_update =
    
    st.sidebar.subheader("Materias Disponibles")
    for subject in sorted(subjects):
        is_active = st.sidebar.checkbox(
            subject, 
            value=(subject in st.session_state['active_subjects']),
            key=f"chk_{subject}"
        )
        if is_active:
            active_subjects_update.append(subject)

    st.session_state['active_subjects'] = active_subjects_update

    # Configuración de estilo del LLM (Simulación de rol, aunque no afecte al LLM Falso)
    st.sidebar.subheader("Estilo de Conversación (Simulado)")
    style = st.sidebar.selectbox(
        "Elige un rol para el tutor:",
       , 
        index=0
    )
    st.session_state['llm_style'] = style
    
    return st.session_state['active_subjects']

def main():
    st.set_page_config(page_title="Tutor RAG Gratuito (Estilo NotebookLM)", layout="wide")
    st.title("👨‍🏫 Tutor Temático RAG: Aprendizaje Adaptativo (Versión Gratuita)")

    # 1. Obtener la lista de materias disponibles
    subjects = get_subjects()
    if not subjects:
         st.error("No se encontraron subdirectorios de materias en 'conocimiento/'.")
         st.stop()

    # 2. Inicializar Vector Store (con caché)
    vector_store = get_vector_store()

    # 3. Configurar barra lateral y obtener materias activas
    active_subjects = sidebar_config(subjects)
    
    if not active_subjects:
        st.sidebar.info("⚠️ No hay materias seleccionadas.")
    else:
        st.sidebar.success(f"Fuentes activas: {len(active_subjects)}/{len(subjects)}")

    # 4. Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state["messages"] =

    # 5. Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. Procesar entrada del usuario
    if prompt := st.chat_input("Pregunta sobre las materias seleccionadas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if not active_subjects:
                 response_content = "Necesitas seleccionar fuentes activas en el panel lateral para que el tutor pueda responder."
                 st.markdown(response_content)
                 st.session_state.messages.append({"role": "assistant", "content": response_content})
                 return

            # 6.1 Construir el RAG Chain dinámico con el LLM FALSO
            rag_chain = get_rag_chain(vector_store, active_subjects)

            # 6.2 Ejecutar la cadena RAG
            with st.spinner("Buscando fuentes relevantes..."):
                # No se necesita un prompt de sistema, ya que el LLM es falso
                response = rag_chain.invoke({"query": prompt})
            
            full_response = response['result']
            
            # 6.3 Post-procesamiento para CITACIONES (ESTO ES REAL)
            citations =
            if response.get("source_documents"):
                citations.append("\n\n---\n\n**Fuentes Citadas (Estilo NotebookLM - RAG Real):**")
                
                # Procesar cada documento recuperado
                for i, doc in enumerate(response["source_documents"]):
                    source_path = doc.metadata.get("source", "Fuente Desconocida")
                    subject_name = doc.metadata.get("subject", "General")
                    file_name = os.path.basename(source_path)
                    
                    citation_text = f"**[{i+1}]** Materia: *{subject_name}*. Archivo: `{file_name}`."
                    citations.append(citation_text)
                    
            # 6.4 Mostrar la respuesta completa (texto simulado + citas reales)
            final_content = full_response + "\n".join(citations)
            st.markdown(final_content)
            
            # 7. Actualizar historial de chat
            st.session_state.messages.append({"role": "assistant", "content": final_content})

if __name__ == "__main__":
    main()
