# app.py

import os
import re
import streamlit as st
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

# --- Constantes de Configuración ---
KNOWLEDGE_PATH = "conocimiento/"
CHROMA_PERSIST_DIR = "chroma_db"
LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/text-embedding-004"

def get_api_key():
    """Obtiene la clave API de forma segura a través de st.secrets."""
    try:
        return st.secrets
    except KeyError:
        st.error("Error: La clave GOOGLE_API_KEY no está configurada en st.secrets.")
        st.stop()

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
def get_vector_store(api_key):
    """Inicializa o carga la base de datos vectorial persistida y cacheada."""
    
    embeddings = GoogleGenAIEmbeddings(model=EMBEDDING_MODEL, api_key=api_key)

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
        with st.spinner("Indexando documentos por primera vez (puede tardar)..."):
            
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
    
    # Crea una lista de cláusulas OR/IN para los subjects seleccionados
    filter_clauses = [{"subject": {"$eq": sub}} for sub in active_subjects]
    return {"$or": filter_clauses}


def get_rag_chain(vector_store, api_key, active_subjects: list):
    """Construye la cadena RAG con el retriever filtrado."""
    
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        api_key=api_key,
        temperature=0.1,
        streaming=False # Simplificamos a no-streaming para usar RetrievalQA
    )

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

    # Configuración de estilo del LLM
    st.sidebar.subheader("Estilo de Conversación")
    style = st.sidebar.selectbox(
        "Elige un rol para el tutor:",
       ,
        index=0
    )
    st.session_state['llm_style'] = style
    
    return st.session_state['active_subjects']

def main():
    st.set_page_config(page_title="Tutor RAG (Estilo NotebookLM)", layout="wide")
    st.title("👨‍🏫 Tutor Temático RAG: Aprendizaje Adaptativo")

    # 1. Cargar secretos y verificar API Key
    api_key = get_api_key()

    # 2. Obtener la lista de materias disponibles
    subjects = get_subjects()
    if not subjects:
         st.error("No se encontraron subdirectorios de materias en 'conocimiento/'.")
         st.stop()

    # 3. Inicializar Vector Store (con caché)
    vector_store = get_vector_store(api_key)

    # 4. Configurar barra lateral y obtener materias activas
    active_subjects = sidebar_config(subjects)
    
    if not active_subjects:
        st.sidebar.info("⚠️ No hay materias seleccionadas.")
    else:
        st.sidebar.success(f"Fuentes activas: {len(active_subjects)}/{len(subjects)}")

    # 5. Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state["messages"] =

    # 6. Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 7. Procesar entrada del usuario
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

            # 7.1 Construir el RAG Chain dinámico con el filtro
            rag_chain = get_rag_chain(vector_store, api_key, active_subjects)

            # 7.2 Insertar prompt de estilo para contextualización
            system_prompt = f"Tu rol es el de un {st.session_state['llm_style']}. Utiliza únicamente la información proporcionada en el contexto para responder la siguiente pregunta, sé detallado y útil:"
            full_prompt = f"{system_prompt}\n\nPregunta: {prompt}"

            # 7.3 Ejecutar la cadena RAG
            with st.spinner("Buscando y generando respuesta..."):
                response = rag_chain.invoke({"query": full_prompt})
            
            full_response = response['result']
            
            # 7.4 Post-procesamiento para CITACIONES
            citations =
            if response.get("source_documents"):
                citations.append("\n\n---\n\n**Fuentes Citadas (Estilo NotebookLM):**")
                
                # Procesar cada documento recuperado
                for i, doc in enumerate(response["source_documents"]):
                    source_path = doc.metadata.get("source", "Fuente Desconocida")
                    subject_name = doc.metadata.get("subject", "General")
                    file_name = os.path.basename(source_path)
                    
                    citation_text = f"**[{i+1}]** Materia: *{subject_name}*. Archivo: `{file_name}`."
                    citations.append(citation_text)
                    
            # 7.5 Mostrar la respuesta completa (texto + citas)
            final_content = full_response + "\n".join(citations)
            st.markdown(final_content)
            
            # 8. Actualizar historial de chat
            st.session_state.messages.append({"role": "assistant", "content": final_content})

if __name__ == "__main__":
    main()
