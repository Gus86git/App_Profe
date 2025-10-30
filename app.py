import streamlit as st
from groq import Groq
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =========================================
# CONFIGURACIÓN DE MATERIAS Y PROFESORES IFTS33
# =========================================
PROFESORES = {
    "estadistica": {
        "nombre_materia": "Estadística y Probabilidad",
        "nombre_profesor": "Profesor Ferrare", 
        "emoji": "📊",
        "estilo": "Práctico y conciso",
        "personalidad": "Eres práctico, directo y te enfocas en ejercicios numéricos. Usa ejemplos concretos de probabilidad y estadística.",
        "carpeta": "estadistica y probabilidad"  # ← NUEVO: nombre exacto de la carpeta
    },
    "desarrollo_ia": {
        "nombre_materia": "Desarrollo de sistemas de IA",
        "nombre_profesor": "Profesora Pose",
        "emoji": "🤖", 
        "estilo": "Técnica y práctica",
        "personalidad": "Eres técnica pero accesible. Enfócate en fundamentos de IA y desarrollo de sistemas inteligentes.",
        "carpeta": "desarrollo de sistemas de ia"  # ← NUEVO: nombre exacto de la carpeta
    },
    "campo_laboral": {
        "nombre_materia": "Aproximación al campo laboral", 
        "nombre_profesor": "Profesora Acri",
        "emoji": "💼",
        "estilo": "Exigente y profesional",
        "personalidad": "Eres exigente pero constructiva. Enfócate en profesionalismo y preparación para el mundo laboral.",
        "carpeta": "aproximacion al campo laboral"  # ← NUEVO: nombre exacto de la carpeta
    },
    "comunicacion": {
        "nombre_materia": "Comunicación",
        "nombre_profesor": "Profesora Rodríguez", 
        "emoji": "💬",
        "estilo": "Clara y comprensible",
        "personalidad": "Eres clara y comprensiblea. Usa ejemplos y técnicas prácticas de comunicación efectiva.",
        "carpeta": "comunicacion"  # ← NUEVO: nombre exacto de la carpeta
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="IA Assistant IFTS33",
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
    st.info("🔑 Configura groq_api_key en los secrets de Streamlit Cloud")
    st.stop()

# =========================================
# SISTEMA DE CONOCIMIENTO HÍBRIDO (ACTUALIZADO)
# =========================================
class SistemaConocimientoHibrido:
    def __init__(self):
        self.documentos = []
        self.metadata = []
        self.vectorizer = None
        self.matriz_tfidf = None
        self.conocimiento_cargado = False
    
    def cargar_conocimiento_completo(self, base_path="conocimiento"):
        """Cargar conocimiento - AHORA COMPATIBLE CON ESPACIOS EN NOMBRES"""
        try:
            if not os.path.exists(base_path):
                return False
            
            self.documentos = []
            self.metadata = []
            
            # NUEVO: Usar el mapeo de PROFESORES para encontrar las carpetas
            for clave, profesor_info in PROFESORES.items():
                nombre_carpeta = profesor_info["carpeta"]
                materia_path = os.path.join(base_path, nombre_carpeta)
                
                if os.path.exists(materia_path):
                    for archivo in os.listdir(materia_path):
                        if archivo.endswith('.txt'):
                            archivo_path = os.path.join(materia_path, archivo)
                            try:
                                with open(archivo_path, 'r', encoding='utf-8') as f:
                                    contenido = f.read()
                                    # PÁRRAFOS LARGOS
                                    parrafos = self._dividir_en_parrafos_largos(contenido)
                                    for i, parrafo in enumerate(parrafos):
                                        if len(parrafo.strip()) > 100:
                                            self.documentos.append(parrafo)
                                            self.metadata.append({
                                                'materia': clave,  # Usamos la clave interna
                                                'archivo': archivo,
                                                'parrafo_num': i,
                                                'fuente': f"{nombre_carpeta}/{archivo}",  # Mostrar nombre real
                                                'longitud': len(parrafo)
                                            })
                            except Exception as e:
                                st.warning(f"⚠️ Error leyendo {archivo_path}: {str(e)}")
                                continue
                else:
                    st.warning(f"📁 No se encuentra: {materia_path}")
            
            if not self.documentos:
                return False
            
            # Sistema de búsqueda optimizado
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                stop_words=['el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'se', 'un', 'una', 'es', 'son'],
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9
            )
            
            self.matriz_tfidf = self.vectorizer.fit_transform(self.documentos)
            self.conocimiento_cargado = True
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error cargando conocimiento: {str(e)}")
            return False
    
    def _dividir_en_parrafos_largos(self, texto):
        """Dividir en párrafos largos manteniendo contexto"""
        parrafos = re.split(r'\n\s*\n', texto)
        parrafos_largos = []
        
        for parrafo in parrafos:
            parrafo = parrafo.strip()
            if len(parrafo) > 100:
                palabras = parrafo.split()
                for i in range(0, len(palabras), 500):
                    chunk = ' '.join(palabras[i:i+500])
                    if len(chunk) > 100:
                        parrafos_largos.append(chunk)
            elif len(parrafo) > 50:
                parrafos_largos.append(parrafo)
        
        return parrafos_largos
    
    def buscar_conocimiento_relevante(self, consulta, materia_filtro=None, top_n=2):
        """Buscar conocimiento local relevante"""
        if not self.conocimiento_cargado or not self.documentos:
            return []
        
        try:
            consulta_tfidf = self.vectorizer.transform([consulta.lower()])
            similitudes = cosine_similarity(consulta_tfidf, self.matriz_tfidf).flatten()
            
            indices_ordenados = similitudes.argsort()[::-1]
            
            resultados = []
            for idx in indices_ordenados:
                if similitudes[idx] > 0.15:
                    metadata = self.metadata[idx]
                    
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
            return []

# =========================================
# INTERFAZ PRINCIPAL (IGUAL QUE ANTES)
# =========================================
def main():
    st.title("🎓 IA Assistant IFTS33")
    st.markdown("### 🤖 Prioriza tu conocimiento + 🧠 IA como complemento")
    
    # Inicializar sistema
    if "sistema_hibrido" not in st.session_state:
        st.session_state.sistema_hibrido = SistemaConocimientoHibrido()
    
    # Cargar conocimiento
    with st.spinner("📚 Cargando conocimiento..."):
        if not st.session_state.sistema_hibrido.conocimiento_cargado:
            cargado = st.session_state.sistema_hibrido.cargar_conocimiento_completo()
            if cargado:
                st.success(f"✅ {len(st.session_state.sistema_hibrido.documentos)} párrafos cargados")
            else:
                st.error("❌ No se pudo cargar el conocimiento")
    
    # Sidebar personalizado
    with st.sidebar:
        st.header("📚 Materias IFTS33")
        
        selected_materia = st.selectbox(
            "Elige tu materia:",
            list(PROFESORES.keys()),
            format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre_materia']}"
        )
        
        profesor = PROFESORES[selected_materia]
        st.subheader(f"{profesor['emoji']} {profesor['nombre_profesor']}")
        st.write(f"**Estilo:** {profesor['estilo']}")
        
        # Configuración avanzada
        st.markdown("---")
        st.subheader("⚙️ Configuración Avanzada")
        
        modelo = st.selectbox(
            "Modelo Groq:",
            [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant", 
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            index=0
        )
        
        modo_respuesta = st.radio(
            "Modo de respuesta:",
            ["🚀 Híbrido (Recomendado)", "📚 Solo conocimiento local", "🧠 Solo IA"],
            index=0,
            help="Híbrido: Prioriza tu conocimiento y usa IA para complementar"
        )
        
        temperatura = st.slider("Creatividad:", 0.1, 1.0, 0.7, 0.1)
        
        # Estadísticas
        st.markdown("---")
        st.subheader("📊 Conocimiento")
        
        if st.session_state.sistema_hibrido.conocimiento_cargado:
            total_parrafos = len(st.session_state.sistema_hibrido.documentos)
            parrafos_materia = sum(1 for m in st.session_state.sistema_hibrido.metadata 
                                 if m['materia'] == selected_materia)
            
            st.metric("Párrafos totales", total_parrafos)
            st.metric(f"Párrafos {selected_materia}", parrafos_materia)
        else:
            st.error("❌ Sin conocimiento cargado")
        
        st.markdown("---")
        
        if st.button("🔄 Recargar Conocimiento", use_container_width=True):
            st.session_state.sistema_hibrido = SistemaConocimientoHibrido()
            st.rerun()
        
        if st.button("🧹 Limpiar Chat", use_container_width=True):
            chat_key = f"messages_{selected_materia}"
            if chat_key in st.session_state:
                st.session_state[chat_key] = []
            st.rerun()
    
    # Inicializar chat
    chat_key = f"messages_{selected_materia}"
    if chat_key not in st.session_state:
        profesor = PROFESORES[selected_materia]
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"¡Hola! Soy {profesor['nombre_profesor']} {profesor['emoji']}. Uso principalmente tu material y complemento con IA cuando es útil. ¿En qué puedo ayudarte con {profesor['nombre_materia'].lower()}?"}
        ]
    
    # Mostrar historial
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Procesar preguntas - SISTEMA HÍBRIDO
    if prompt := st.chat_input(f"Pregunta sobre {PROFESORES[selected_materia]['nombre_materia']}..."):
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner(f"🔍 {PROFESORES[selected_materia]['nombre_profesor']} analiza..."):
                try:
                    profesor = PROFESORES[selected_materia]
                    
                    # BUSCAR EN CONOCIMIENTO LOCAL
                    resultados_locales = st.session_state.sistema_hibrido.buscar_conocimiento_relevante(
                        prompt, selected_materia
                    )
                    
                    # CONSTRUIR RESPUESTA SEGÚN MODO
                    if modo_respuesta == "📚 Solo conocimiento local":
                        respuesta = generar_respuesta_solo_local(prompt, selected_materia, resultados_locales, profesor)
                    
                    elif modo_respuesta == "🧠 Solo IA":
                        respuesta = generar_respuesta_solo_ia(prompt, selected_materia, profesor, modelo, temperatura)
                    
                    else:  # MODO HÍBRIDO
                        respuesta = generar_respuesta_hibrida(
                            prompt, selected_materia, resultados_locales, profesor, modelo, temperatura
                        )
                    
                    # Mostrar respuesta
                    st.markdown(respuesta)
                    st.session_state[chat_key].append({"role": "assistant", "content": respuesta})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[chat_key].append({"role": "assistant", "content": error_msg})

# =========================================
# FUNCIONES DE GENERACIÓN DE RESPUESTAS (IGUALES)
# =========================================
def generar_respuesta_solo_local(prompt, materia, resultados, profesor):
    """Respuesta usando solo conocimiento local"""
    if resultados:
        respuesta = f"**{profesor['emoji']} {profesor['nombre_profesor']} responde (basado en tu material):**\n\n"
        
        for i, resultado in enumerate(resultados, 1):
            similitud_porcentaje = resultado['similitud'] * 100
            respuesta += f"**📚 De {resultado['metadata']['fuente']}** ({similitud_porcentaje:.1f}% relevante):\n"
            respuesta += f"{resultado['contenido']}\n\n"
        
        respuesta += f"**🎯 {profesor['nombre_profesor']}:** Esta información viene directamente de tu material de estudio."
        
    else:
        respuesta = f"**{profesor['emoji']} {profesor['nombre_profesor']}:**\n\n"
        respuesta += "❌ **No encontré información específica sobre esto en tu material.**\n\n"
        respuesta += "💡 *Sugerencia:* Agrega contenido sobre este tema a la carpeta 'conocimiento' o prueba el modo híbrido."
    
    return respuesta

def generar_respuesta_solo_ia(prompt, materia, profesor, modelo, temperatura):
    """Respuesta usando solo IA (como respaldo)"""
    try:
        prompt_ia = f"""
        Eres {profesor['nombre_profesor']}, especialista en {profesor['nombre_materia']}.
        {profesor['personalidad']}
        
        Responde la siguiente pregunta manteniendo tu estilo característico.
        Sé práctico y útil para el estudiante.
        
        PREGUNTA: {prompt}
        
        RESPUESTA:
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_ia}],
            model=modelo,
            temperature=temperatura,
            max_tokens=800
        )
        
        respuesta_ia = response.choices[0].message.content
        
        return f"**{profesor['emoji']} {profesor['nombre_profesor']} responde (usando conocimiento general):**\n\n{respuesta_ia}\n\n*💡 Nota: Esta respuesta viene del modelo IA, no de tu material específico.*"
    
    except Exception as e:
        return f"❌ Error al generar respuesta con IA: {str(e)}"

def generar_respuesta_hibrida(prompt, materia, resultados, profesor, modelo, temperatura):
    """Respuesta híbrida - Prioriza local, complementa con IA"""
    
    # Construir base con conocimiento local
    respuesta = f"**{profesor['emoji']} {profesor['nombre_profesor']} responde:**\n\n"
    
    if resultados:
        # USAR CONOCIMIENTO LOCAL COMO BASE PRINCIPAL
        respuesta += "**📚 Basado en tu material:**\n\n"
        
        for i, resultado in enumerate(resultados, 1):
            similitud_porcentaje = resultado['similitud'] * 100
            respuesta += f"**De {resultado['metadata']['fuente']}** ({similitud_porcentaje:.1f}% relevante):\n"
            respuesta += f"{resultado['contenido']}\n\n"
        
        # COMPLEMENTAR CON IA PARA CONTEXTUALIZAR
        try:
            prompt_complemento = f"""
            Eres {profesor['nombre_profesor']}. Acabo de proporcionar al estudiante información específica de su material sobre: "{prompt}"
            
            INFORMACIÓN PROPORCIONADA (de su material):
            {''.join([r['contenido'][:500] + '...' for r in resultados])}
            
            Tu tarea es: 
            1. Contextualizar esta información
            2. Dar ejemplos adicionales RELACIONADOS
            3. Proporcionar consejos prácticos
            4. Mantenerte dentro del tema y NO introducir conceptos nuevos
            
            Responde de manera natural como {profesor['nombre_profesor']} lo haría.
            """
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_complemento}],
                model=modelo,
                temperature=temperatura * 0.7,  # Menos creatividad para complementos
                max_tokens=400
            )
            
            complemento_ia = response.choices[0].message.content
            
            respuesta += f"**💡 Complemento contextual:**\n{complemento_ia}\n\n"
            respuesta += f"**🎯 {profesor['nombre_profesor']}:** Recuerda revisar tu material completo para más detalles."
            
        except Exception as e:
            respuesta += f"*💡 He proporcionado la información de tu material. Revisa los archivos para más detalles.*"
    
    else:
        # SI NO HAY CONOCIMIENTO LOCAL, USAR IA PERO SER TRANSPARENTE
        respuesta += "**📝 No encontré información específica en tu material, pero basándome en el tema:**\n\n"
        
        try:
            prompt_ia_cauteloso = f"""
            Eres {profesor['nombre_profesor']}. Un estudiante te pregunta sobre: "{prompt}"
            
            IMPORTANTE: No hay información específica en su material sobre esto.
            Responde de manera general pero ÚTIL, y:
            - Enfócate en conceptos básicos relacionados
            - Sugiere qué tipo de contenido debería agregar a su material
            - No inventes información detallada o específica
            - Sé honesto sobre las limitaciones
            
            Responde como {profesor['nombre_profesor']} lo haría.
            """
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_ia_cauteloso}],
                model=modelo,
                temperature=temperatura * 0.5,  # Muy baja creatividad
                max_tokens=500
            )
            
            respuesta_ia = response.choices[0].message.content
            respuesta += f"{respuesta_ia}\n\n"
            respuesta += "**💡 Sugerencia:** Considera agregar contenido sobre este tema a tu carpeta 'conocimiento' para respuestas más específicas."
            
        except Exception as e:
            respuesta += "❌ No pude generar una respuesta complementaria en este momento."
    
    return respuesta

if __name__ == "__main__":
    main()
