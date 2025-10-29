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
        "estilo": "Práctico y numérico"
    },
    "desarrollo_ia": {
        "nombre": "Especialista IA", 
        "emoji": "🤖",
        "estilo": "Técnico y práctico"
    },
    "campo_laboral": {
        "nombre": "Profesora Acri",
        "emoji": "💼", 
        "estilo": "Exigente y profesional"
    },
    "comunicacion": {
        "nombre": "Especialista Comunicación",
        "emoji": "🎯",
        "estilo": "Claro y estructurado"
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias - Solo Tu Conocimiento",
    page_icon="🎓",
    layout="wide"
)

# =========================================
# INICIALIZAR GROQ
# =========================================
try:
    client = Groq(api_key=st.secrets["Ggroq_api_key"])
except Exception as e:
    st.error(f"❌ Error configurando Groq: {str(e)}")
    st.info("🔑 Configura GROQ_API_KEY en los secrets de Streamlit Cloud")
    st.stop()

# =========================================
# SISTEMA DE CONOCIMIENTO ESTRICTO
# =========================================
class SistemaConocimientoEstricto:
    def __init__(self):
        self.documentos = []
        self.metadata = []
        self.vectorizer = None
        self.matriz_tfidf = None
        self.conocimiento_cargado = False
    
    def cargar_todo_el_conocimiento(self, base_path="conocimiento"):
        """Cargar ABSOLUTAMENTE TODO el conocimiento disponible"""
        try:
            if not os.path.exists(base_path):
                return False
            
            self.documentos = []
            self.metadata = []
            
            # Cargar recursivamente todo el contenido
            for materia in os.listdir(base_path):
                materia_path = os.path.join(base_path, materia)
                if os.path.isdir(materia_path):
                    for archivo in os.listdir(materia_path):
                        if archivo.endswith(('.txt', '.md')):
                            archivo_path = os.path.join(materia_path, archivo)
                            try:
                                with open(archivo_path, 'r', encoding='utf-8') as f:
                                    contenido = f.read()
                                    # Procesar cada línea/párrafo individualmente
                                    lineas = self._procesar_lineas(contenido)
                                    for i, linea in enumerate(lineas):
                                        if len(linea.strip()) > 20:  # Líneas significativas
                                            self.documentos.append(linea)
                                            self.metadata.append({
                                                'materia': materia,
                                                'archivo': archivo,
                                                'linea_num': i,
                                                'fuente': f"{materia}/{archivo}",
                                                'contenido_completo': linea
                                            })
                            except Exception as e:
                                continue
            
            if not self.documentos:
                return False
            
            # Sistema de búsqueda más preciso
            self.vectorizer = TfidfVectorizer(
                max_features=1500,
                stop_words=['el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'se', 'un', 'una', 'es', 'son'],
                ngram_range=(1, 3),  # Incluir trigramas para más precisión
                min_df=1,
                max_df=0.85
            )
            
            self.matriz_tfidf = self.vectorizer.fit_transform(self.documentos)
            self.conocimiento_cargado = True
            
            return True
            
        except Exception as e:
            return False
    
    def _procesar_lineas(self, texto):
        """Dividir texto en líneas/párrafos individuales"""
        # Dividir por saltos de línea y puntos
        lineas = re.split(r'\n|\.\s+', texto)
        return [linea.strip() for linea in lineas if len(linea.strip()) > 10]
    
    def buscar_respuesta_estricta(self, consulta, materia_filtro=None, umbral_similitud=0.25):
        """Buscar SOLO en el conocimiento local - Modo estricto"""
        if not self.conocimiento_cargado or not self.documentos:
            return None, []
        
        try:
            # Transformar la consulta
            consulta_tfidf = self.vectorizer.transform([consulta.lower()])
            
            # Calcular similitudes
            similitudes = cosine_similarity(consulta_tfidf, self.matriz_tfidf).flatten()
            
            # Encontrar la mejor coincidencia
            mejor_idx = similitudes.argmax()
            mejor_similitud = similitudes[mejor_idx]
            
            # Solo considerar si supera el umbral
            if mejor_similitud > umbral_similitud:
                mejor_resultado = {
                    'contenido': self.documentos[mejor_idx],
                    'metadata': self.metadata[mejor_idx],
                    'similitud': mejor_similitud
                }
                
                # Buscar resultados adicionales relevantes
                resultados_adicionales = []
                for idx in similitudes.argsort()[::-1][1:4]:  # Top 3 adicionales
                    if similitudes[idx] > umbral_similitud:
                        metadata = self.metadata[idx]
                        # Filtrar por materia si se especifica
                        if materia_filtro and metadata['materia'] != materia_filtro:
                            continue
                        resultados_adicionales.append({
                            'contenido': self.documentos[idx],
                            'metadata': metadata,
                            'similitud': similitudes[idx]
                        })
                
                return mejor_resultado, resultados_adicionales
            else:
                return None, []
            
        except Exception as e:
            return None, []

# =========================================
# INTERFAZ PRINCIPAL ESTRICTA
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias - SOLO Tu Conocimiento")
    st.markdown("### 🤖 **Modo Estricto**: Solo responde basado en tu material 📚")
    
    # Inicializar sistema de conocimiento estricto
    if "sistema_estricto" not in st.session_state:
        st.session_state.sistema_estricto = SistemaConocimientoEstricto()
    
    # Cargar conocimiento
    with st.spinner("📚 Cargando TODO tu conocimiento..."):
        if not st.session_state.sistema_estricto.conocimiento_cargado:
            cargado = st.session_state.sistema_estricto.cargar_todo_el_conocimiento()
            if cargado:
                st.success(f"✅ Cargados {len(st.session_state.sistema_estricto.documentos)} fragmentos de conocimiento")
            else:
                st.error("❌ No se pudo cargar el conocimiento. Verifica la carpeta 'conocimiento/'")
    
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
        
        # Configuración estricta
        st.markdown("---")
        st.subheader("🎯 Modo Estricto")
        
        umbral = st.slider(
            "Umbral de similitud:",
            min_value=0.1,
            max_value=0.5,
            value=0.25,
            step=0.05,
            help="Mayor valor = más estricto (solo responde si encuentra contenido muy similar)"
        )
        
        # Estadísticas del conocimiento
        st.markdown("---")
        st.subheader("📊 Tu Conocimiento")
        
        if st.session_state.sistema_estricto.conocimiento_cargado:
            total_fragmentos = len(st.session_state.sistema_estricto.documentos)
            fragmentos_materia = sum(1 for m in st.session_state.sistema_estricto.metadata 
                                   if m['materia'] == selected_materia)
            
            st.success(f"📚 {total_fragmentos} fragmentos")
            st.info(f"📖 {fragmentos_materia} en {selected_materia}")
            
            # Mostrar archivos disponibles
            st.markdown("**📁 Archivos cargados:**")
            archivos_por_materia = {}
            for meta in st.session_state.sistema_estricto.metadata:
                if meta['materia'] == selected_materia:
                    if meta['archivo'] not in archivos_por_materia:
                        archivos_por_materia[meta['archivo']] = 0
                    archivos_por_materia[meta['archivo']] += 1
            
            for archivo, count in list(archivos_por_materia.items())[:5]:  # Mostrar primeros 5
                st.write(f"• {archivo} ({count} fragmentos)")
            
            if len(archivos_por_materia) > 5:
                st.write(f"• ... y {len(archivos_por_materia) - 5} más")
        else:
            st.error("❌ Sin conocimiento cargado")
        
        st.markdown("---")
        
        if st.button("🔄 Recargar Conocimiento", use_container_width=True):
            st.session_state.sistema_estricto = SistemaConocimientoEstricto()
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
            {"role": "assistant", "content": f"¡Hola! Soy {profesor['nombre']} {profesor['emoji']}. **Solo responderé basado en tu material específico**. ¿En qué puedo ayudarte?"}
        ]
    
    # Mostrar historial de chat
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Procesar preguntas - MODO ESTRICTO
    if prompt := st.chat_input(f"Pregunta sobre {selected_materia.replace('_', ' ')}..."):
        # Agregar mensaje del usuario
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta - SOLO CONOCIMIENTO LOCAL
        with st.chat_message("assistant"):
            with st.spinner(f"🔍 Buscando en tu material..."):
                try:
                    # BUSCAR ESTRICTAMENTE en el conocimiento local
                    mejor_resultado, resultados_adicionales = st.session_state.sistema_estricto.buscar_respuesta_estricta(
                        prompt, selected_materia, umbral
                    )
                    
                    if mejor_resultado:
                        # CONSTRUIR RESPUESTA BASADA SOLO EN EL CONOCIMIENTO LOCAL
                        respuesta = f"**{PROFESORES[selected_materia]['emoji']} {PROFESORES[selected_materia]['nombre']} responde:**\n\n"
                        
                        # Agregar el mejor resultado
                        respuesta += f"📚 **Según tu material** ({mejor_resultado['metadata']['fuente']} - {mejor_resultado['similitud']:.1%} de similitud):\n"
                        respuesta += f"{mejor_resultado['contenido']}\n\n"
                        
                        # Agregar resultados adicionales si existen
                        if resultados_adicionales:
                            respuesta += "**💡 Información relacionada:**\n"
                            for i, resultado in enumerate(resultados_adicionales, 1):
                                respuesta += f"\n{i}. **De {resultado['metadata']['fuente']}**: {resultado['contenido'][:150]}...\n"
                        
                        # Consejo específico basado en el contenido
                        respuesta += f"\n**🎯 {PROFESORES[selected_materia]['nombre']} aconseja:** Revisa tu material específico para más detalles."
                        
                    else:
                        # NO HAY INFORMACIÓN SUFICIENTE - MODO ESTRICTO
                        respuesta = f"**{PROFESORES[selected_materia]['emoji']} {PROFESORES[selected_materia]['nombre']}:**\n\n"
                        respuesta += "❌ **No encontré información específica sobre esto en tu material.**\n\n"
                        respuesta += "**📝 Sugerencias:**\n"
                        respuesta += "• Revisa si el tema está cubierto en tus archivos\n"
                        respuesta += "• Agrega más contenido a la carpeta 'conocimiento'\n"
                        respuesta += "• Reformula tu pregunta usando términos de tu material\n"
                        respuesta += f"• Verifica los archivos en '{selected_materia}/'"
                    
                    # Mostrar respuesta
                    st.markdown(respuesta)
                    
                    # Agregar al historial
                    st.session_state[chat_key].append({"role": "assistant", "content": respuesta})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
    
    # Footer informativo
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.sistema_estricto.conocimiento_cargado:
            total = len(st.session_state.sistema_estricto.documentos)
            st.success(f"📚 {total} fragmentos")
        else:
            st.error("❌ Sin conocimiento")
    
    with col2:
        st.info(f"🎯 Modo Estricto")
        st.write(f"Umbral: {umbral}")
    
    with col3:
        st.warning("⚠️ Solo responde con tu material")

if __name__ == "__main__":
    main()
