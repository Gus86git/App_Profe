import streamlit as st
from groq import Groq
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =========================================
# CONFIGURACIÓN DE PROFESORES
# =========================================
PROFESORES = {
    "estadistica": {
        "nombre": "Profesor Ferrarre",
        "emoji": "📊",
        "estilo": "Práctico y numérico",
        "sistema_prompt_base": """Eres el Profesor Ferrarre, experto en estadística. 
Tu estilo es práctico, directo y motivador. 
Responde en español de manera clara y útil."""
    },
    "desarrollo_ia": {
        "nombre": "Especialista IA", 
        "emoji": "🤖",
        "estilo": "Técnico y práctico", 
        "sistema_prompt_base": """Eres un Especialista en IA técnico y práctico.
Explica conceptos de manera clara, enfócate en fundamentos y proyectos reales.
Responde en español de manera técnica pero accesible."""
    },
    "campo_laboral": {
        "nombre": "Profesora Acri",
        "emoji": "💼", 
        "estilo": "Exigente y profesional",
        "sistema_prompt_base": """Eres la Profesora Acri, exigente pero constructiva.
Enfócate en profesionalismo, preparación para entrevistas y desarrollo career.
Responde en español con un tono profesional y motivador."""
    },
    "comunicacion": {
        "nombre": "Especialista Comunicación",
        "emoji": "🎯",
        "estilo": "Claro y estructurado",
        "sistema_prompt_base": """Eres un Especialista en Comunicación claro y estructurado.
Enseña con ejemplos concretos, enfócate en estructura de mensajes.
Responde en español de manera clara y ejemplificada."""
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias con Conocimiento Real",
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
# SISTEMA DE CONOCIMIENTO RAG
# =========================================
class SistemaConocimiento:
    def __init__(self):
        self.documentos = []
        self.metadata = []  # Para guardar materia y fuente de cada documento
        self.vectorizer = None
        self.matriz_tfidf = None
        self.conocimiento_cargado = False
    
    def cargar_conocimiento_desde_carpeta(self, base_path="conocimiento"):
        """Cargar TODOS los archivos de texto de la carpeta conocimiento"""
        try:
            if not os.path.exists(base_path):
                st.warning("📁 No se encuentra la carpeta 'conocimiento'. Puedes crearla y agregar tus archivos.")
                return False
            
            self.documentos = []
            self.metadata = []
            
            # Recorrer todas las materias y archivos
            for materia in os.listdir(base_path):
                materia_path = os.path.join(base_path, materia)
                if os.path.isdir(materia_path):
                    for archivo in os.listdir(materia_path):
                        if archivo.endswith(('.txt', '.md', '.pdf')):  # Soporta múltiples formatos
                            archivo_path = os.path.join(materia_path, archivo)
                            try:
                                # Por ahora solo txt, pero se puede expandir
                                if archivo.endswith('.txt'):
                                    with open(archivo_path, 'r', encoding='utf-8') as f:
                                        contenido = f.read()
                                        # Dividir en chunks más pequeños para mejor búsqueda
                                        chunks = self._dividir_en_chunks(contenido)
                                        for i, chunk in enumerate(chunks):
                                            if len(chunk.strip()) > 50:  # Chunks significativos
                                                self.documentos.append(chunk)
                                                self.metadata.append({
                                                    'materia': materia,
                                                    'archivo': archivo,
                                                    'chunk_num': i,
                                                    'fuente': f"{materia}/{archivo}"
                                                })
                            except Exception as e:
                                st.warning(f"⚠️ Error leyendo {archivo_path}: {str(e)}")
                                continue
            
            if not self.documentos:
                st.warning("📝 No se encontraron archivos de texto en la carpeta conocimiento")
                return False
            
            # Crear sistema de búsqueda semántica
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=['el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'se'],
                ngram_range=(1, 2)
            )
            
            self.matriz_tfidf = self.vectorizer.fit_transform(self.documentos)
            self.conocimiento_cargado = True
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error cargando conocimiento: {str(e)}")
            return False
    
    def _dividir_en_chunks(self, texto, chunk_size=500):
        """Dividir texto en chunks manejables"""
        palabras = texto.split()
        chunks = []
        for i in range(0, len(palabras), chunk_size):
            chunk = ' '.join(palabras[i:i+chunk_size])
            chunks.append(chunk)
        return chunks
    
    def buscar_conocimiento_relevante(self, consulta, materia_filtro=None, top_n=3):
        """Buscar los documentos más relevantes para una consulta"""
        if not self.conocimiento_cargado or not self.documentos:
            return []
        
        try:
            # Transformar la consulta
            consulta_tfidf = self.vectorizer.transform([consulta])
            
            # Calcular similitudes
            similitudes = cosine_similarity(consulta_tfidf, self.matriz_tfidf).flatten()
            
            # Obtener índices ordenados por similitud
            indices_ordenados = similitudes.argsort()[::-1]
            
            resultados = []
            for idx in indices_ordenados:
                if similitudes[idx] > 0.1:  # Umbral mínimo de similitud
                    metadata = self.metadata[idx]
                    
                    # Filtrar por materia si se especifica
                    if materia_filtro and metadata['materia'] != materia_filtro:
                        continue
                    
                    resultados.append({
                        'contenido': self.documentos[idx],
                        'metadata': metadata,
                        'similitud': similitudes[idx]
                    })
                    
                    if len(resultados) >= top_n:
                        break
            
            return resultados
            
        except Exception as e:
            st.error(f"❌ Error en búsqueda: {str(e)}")
            return []

# =========================================
# INTERFAZ PRINCIPAL MEJORADA
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias - Con Conocimiento Real")
    st.markdown("### 🤖 IA + 📚 Tu Material = Respuestas Perfectas")
    
    # Inicializar sistema de conocimiento
    if "sistema_conocimiento" not in st.session_state:
        st.session_state.sistema_conocimiento = SistemaConocimiento()
    
    # Cargar conocimiento
    with st.spinner("📚 Cargando tu conocimiento personalizado..."):
        if not st.session_state.sistema_conocimiento.conocimiento_cargado:
            st.session_state.sistema_conocimiento.cargar_conocimiento_desde_carpeta()
    
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
        
        # Estadísticas del conocimiento
        st.markdown("---")
        st.subheader("📊 Tu Conocimiento")
        
        if st.session_state.sistema_conocimiento.conocimiento_cargado:
            total_docs = len(st.session_state.sistema_conocimiento.documentos)
            docs_materia = sum(1 for m in st.session_state.sistema_conocimiento.metadata 
                             if m['materia'] == selected_materia)
            
            st.success(f"📚 {total_docs} chunks de conocimiento")
            st.info(f"📖 {docs_materia} chunks en {selected_materia}")
        else:
            st.warning("💡 Agrega archivos a la carpeta 'conocimiento'")
        
        st.markdown("---")
        st.subheader("⚙️ Configuración")
        
        modelo = st.selectbox(
            "Modelo Groq:",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0
        )
        
        usar_conocimiento = st.toggle("Usar conocimiento local", value=True)
        
        st.markdown("---")
        
        if st.button("🔄 Recargar Conocimiento", use_container_width=True):
            st.session_state.sistema_conocimiento = SistemaConocimiento()
            st.rerun()
        
        if st.button("🧹 Limpiar Chat", use_container_width=True):
            chat_key = f"messages_{selected_materia}"
            if chat_key in st.session_state:
                st.session_state[chat_key] = []
            st.rerun()
    
    # Inicializar chat específico por materia
    chat_key = f"messages_{selected_materia}"
    if chat_key not in st.session_state:
        profesor = PROFESORES[selected_materia]
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"¡Hola! Soy {profesor['nombre']} {profesor['emoji']}. Tengo acceso a todo tu material de estudio. ¿En qué puedo ayudarte?"}
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
            with st.spinner(f"🔍 {PROFESORES[selected_materia]['nombre']} busca en tu material..."):
                try:
                    profesor = PROFESORES[selected_materia]
                    
                    # BUSCAR EN EL CONOCIMIENTO LOCAL
                    contexto_conocimiento = ""
                    if usar_conocimiento and st.session_state.sistema_conocimiento.conocimiento_cargado:
                        resultados = st.session_state.sistema_conocimiento.buscar_conocimiento_relevante(
                            prompt, selected_materia, top_n=2
                        )
                        
                        if resultados:
                            contexto_conocimiento = "\n\n--- INFORMACIÓN DE TU MATERIAL ---\n"
                            for i, resultado in enumerate(resultados, 1):
                                contexto_conocimiento += f"\n📚 **De {resultado['metadata']['fuente']}** (relevancia: {resultado['similitud']:.1%}):\n"
                                contexto_conocimiento += f"{resultado['contenido']}\n"
                    
                    # PREPARAR PROMPT INTELIGENTE
                    prompt_final = f"""
                    {profesor['sistema_prompt_base']}
                    
                    CONTEXTO ESPECÍFICO DEL ESTUDIANTE:
                    {contexto_conocimiento if contexto_conocimiento else "No hay información específica en el material. Usa tu conocimiento general."}
                    
                    INSTRUCCIONES IMPORTANTES:
                    - Responde como {profesor['nombre']}
                    - Si hay información en el CONTEXTO, ÚSALA como base principal
                    - Si no hay información específica, usa tu conocimiento general pero menciona que es información general
                    - Sé práctico y útil para aprobar la materia
                    - Mantén tu estilo: {profesor['estilo']}
                    
                    PREGUNTA DEL ESTUDIANTE: {prompt}
                    
                    RESPUESTA:
                    """
                    
                    # Llamar a Groq
                    response = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_final}],
                        model=modelo,
                        temperature=0.7,
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.sistema_conocimiento.conocimiento_cargado:
            total_chunks = len(st.session_state.sistema_conocimiento.documentos)
            st.success(f"📚 {total_chunks} chunks de conocimiento")
        else:
            st.warning("💡 Sin conocimiento local")
    
    with col2:
        st.info(f"🎯 {PROFESORES[selected_materia]['nombre']}")
    
    with col3:
        st.success("🚀 Groq + Tu Material")

if __name__ == "__main__":
    main()
