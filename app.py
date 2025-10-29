import streamlit as st
import os
import time
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

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
    page_title="Asistente 4 Materias + Búsqueda Semántica",
    page_icon="🎓",
    layout="wide"
)

# =========================================
# SISTEMA DE BÚSQUEDA SEMÁNTICA
# =========================================
class SistemaBusqueda:
    def __init__(self):
        self.documentos = []
        self.nombres_docs = []
        self.vectorizer = None
        self.matriz_tfidf = None
    
    def cargar_y_procesar_conocimiento(self):
        """Cargar y procesar todo el conocimiento para búsqueda semántica"""
        try:
            base_path = "conocimiento"
            if not os.path.exists(base_path):
                return False
            
            # Limpiar datos anteriores
            self.documentos = []
            self.nombres_docs = []
            
            # Cargar todos los documentos
            for materia in os.listdir(base_path):
                materia_path = os.path.join(base_path, materia)
                if os.path.isdir(materia_path):
                    for archivo in os.listdir(materia_path):
                        if archivo.endswith('.txt'):
                            archivo_path = os.path.join(materia_path, archivo)
                            try:
                                with open(archivo_path, 'r', encoding='utf-8') as f:
                                    contenido = f.read()
                                    # Dividir en párrafos para búsqueda más precisa
                                    parrafos = self._dividir_en_parrafos(contenido)
                                    for i, parrafo in enumerate(parrafos):
                                        if len(parrafo.strip()) > 50:  # Solo párrafos significativos
                                            self.documentos.append(parrafo)
                                            self.nombres_docs.append(f"{materia}/{archivo} - Párrafo {i+1}")
                            except Exception as e:
                                continue
            
            if not self.documentos:
                return False
            
            # Crear modelo TF-IDF
            self.vectorizer = TfidfVectorizer(
                stop_words=['el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'se', 'no'],
                max_features=1000,
                ngram_range=(1, 2)
            )
            
            self.matriz_tfidf = self.vectorizer.fit_transform(self.documentos)
            return True
            
        except Exception as e:
            st.error(f"❌ Error procesando conocimiento: {str(e)}")
            return False
    
    def _dividir_en_parrafos(self, texto):
        """Dividir texto en párrafos significativos"""
        # Dividir por saltos de línea dobles o puntos seguidos de mayúscula
        parrafos = re.split(r'\n\s*\n|\.\s+[A-Z]', texto)
        return [p.strip() for p in parrafos if p.strip()]
    
    def buscar_similaridad(self, consulta, top_n=3):
        """Buscar los documentos más similares a la consulta"""
        if not self.documentos or self.vectorizer is None:
            return []
        
        try:
            # Transformar la consulta
            consulta_tfidf = self.vectorizer.transform([consulta])
            
            # Calcular similitudes
            similitudes = cosine_similarity(consulta_tfidf, self.matriz_tfidf).flatten()
            
            # Obtener los índices de los más similares
            indices_similares = similitudes.argsort()[-top_n:][::-1]
            
            resultados = []
            for idx in indices_similares:
                if similitudes[idx] > 0.1:  # Umbral mínimo de similitud
                    resultados.append({
                        'contenido': self.documentos[idx],
                        'fuente': self.nombres_docs[idx],
                        'similitud': similitudes[idx]
                    })
            
            return resultados
            
        except Exception as e:
            st.error(f"❌ Error en búsqueda: {str(e)}")
            return []

# =========================================
# FUNCIÓN MEJORADA DE RESPUESTAS
# =========================================
def generar_respuesta_inteligente(pregunta, materia, sistema_busqueda):
    """Generar respuesta usando búsqueda semántica"""
    profesor = PROFESORES[materia]
    
    # Buscar contenido relevante
    resultados = sistema_busqueda.buscar_similaridad(pregunta)
    
    # Filtrar resultados por materia si es posible
    resultados_materia = [r for r in resultados if materia in r['fuente']]
    if not resultados_materia:
        resultados_materia = resultados  # Usar todos si no hay de la materia específica
    
    # Construir respuesta base
    respuesta_base = f"""
    {profesor['emoji']} **{profesor['nombre']} responde:**

    **Sobre tu pregunta:** "{pregunta}"
    """
    
    # Añadir contenido relevante si se encontró
    if resultados_materia:
        respuesta_base += f"\n\n**📚 Encontré información relevante en el material:**\n\n"
        
        for i, resultado in enumerate(resultados_materia[:2], 1):  # Top 2 resultados
            similitud_porcentaje = resultado['similitud'] * 100
            respuesta_base += f"**{i}. De {resultado['fuente']}** (relevancia: {similitud_porcentaje:.1f}%):\n"
            respuesta_base += f"*\"{resultado['contenido'][:250]}...\"*\n\n"
    else:
        # Fallback a consejos del profesor
        respuesta_base += f"\n\n**💡 {random.choice(profesor['consejos'])}**"
        respuesta_base += f"\n\n**🎯 Recuerda:** En {materia.replace('_', ' ')}, {profesor['estilo'].lower()}"
    
    # Añadir estilo y consejo del profesor
    respuesta_base += f"\n\n**🌟 Consejo de {profesor['nombre']}:** {random.choice(profesor['consejos'])}"
    
    return respuesta_base

# =========================================
# INTERFAZ PRINCIPAL MEJORADA
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias + Búsqueda Semántica")
    st.markdown("### Ahora con búsqueda inteligente en todo tu material")
    
    # Inicializar sistema de búsqueda
    if "sistema_busqueda" not in st.session_state:
        st.session_state.sistema_busqueda = SistemaBusqueda()
    
    # Cargar y procesar conocimiento
    with st.spinner("🧠 Procesando conocimiento para búsqueda semántica..."):
        if st.session_state.sistema_busqueda.cargar_y_procesar_conocimiento():
            st.success(f"✅ Sistema de búsqueda listo - {len(st.session_state.sistema_busqueda.documentos)} párrafos procesados")
        else:
            st.warning("⚠️ Sistema funcionando en modo básico - verifica la carpeta 'conocimiento'")
    
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
        
        # Mostrar estadísticas del sistema
        st.markdown("---")
        st.subheader("🔍 Estado del Sistema")
        
        if st.session_state.sistema_busqueda.documentos:
            st.success(f"📊 {len(st.session_state.sistema_busqueda.documentos)} párrafos indexados")
            st.info(f"🔤 {len(st.session_state.sistema_busqueda.vectorizer.get_feature_names_out() if st.session_state.sistema_busqueda.vectorizer else 0)} términos en vocabulario")
        else:
            st.warning("📝 Sin documentos procesados")
        
        # Contar documentos por materia
        st.markdown("**📂 Documentos por materia:**")
        if st.session_state.sistema_busqueda.nombres_docs:
            conteo_materias = {}
            for nombre in st.session_state.sistema_busqueda.nombres_docs:
                materia = nombre.split('/')[0]
                conteo_materias[materia] = conteo_materias.get(materia, 0) + 1
            
            for materia, count in conteo_materias.items():
                emoji = PROFESORES.get(materia, {}).get('emoji', '📄')
                st.write(f"• {emoji} {materia}: {count} párrafos")
        
        st.markdown("---")
        
        if st.button("🔄 Reprocesar Conocimiento", use_container_width=True):
            st.session_state.sistema_busqueda = SistemaBusqueda()
            st.rerun()
        
        if st.button("🧹 Limpiar Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"¡Hola! Soy {PROFESORES[selected_materia]['nombre']} {PROFESORES[selected_materia]['emoji']}. Ahora puedo buscar inteligentemente en todo tu material usando búsqueda semántica. ¿En qué puedo ayudarte?"}
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
            with st.spinner(f"🔍 {PROFESORES[selected_materia]['nombre']} busca semánticamente..."):
                respuesta = generar_respuesta_inteligente(prompt, selected_materia, st.session_state.sistema_busqueda)
                
                # Efecto de escritura
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in respuesta.split():
                    full_response += chunk + " "
                    time.sleep(0.02)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Footer informativo
    st.markdown("---")
    st.success("""
    **🚀 ¡Búsqueda Semántica Implementada!**
    
    **✅ Nuevas capacidades:**
    - Búsqueda por similitud semántica (TF-IDF + Cosine Similarity)
    - Procesamiento inteligente de párrafos
    - Resultados ordenados por relevancia
    - Porcentajes de similitud
    - Vocabulario especializado por materia
    
    **🔍 Cómo funciona:**
    1. **TF-IDF**: Identifica términos importantes en tu material
    2. **Cosine Similarity**: Calcula similitud entre pregunta y contenido
    3. **Ranking**: Ordena resultados por relevancia
    4. **Contexto**: Muestra los párrafos más relevantes
    
    **📈 Próximo paso:** Agregar generación de respuestas con IA
    """)

if __name__ == "__main__":
    main()
