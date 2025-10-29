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
        "personalidad": "Eres directo, técnico y motivador. Enfócate en ejercicios prácticos y procesos paso a paso.",
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
        "personalidad": "Eres preciso, moderno y práctico. Explica conceptos técnicos de manera clara.",
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
        "personalidad": "Eres profesional, directa y orientada a resultados. Sé exigente pero constructiva.",
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
        "personalidad": "Eres amable, organizado y ejemplificador. Enseña con ejemplos concretos.",
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
    page_title="Asistente 4 Materias + IA Avanzada",
    page_icon="🎓",
    layout="wide"
)

# =========================================
# SISTEMA DE IA CON MODELOS LIGEROS
# =========================================
class SistemaIA:
    def __init__(self):
        self.modelo_ia = None
        self.tokenizer = None
    
    def cargar_modelo_ligero(self):
        """Cargar modelo de IA ligero y compatible"""
        try:
            from transformers import pipeline
            
            # Usar un modelo más ligero y rápido
            self.modelo_ia = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-small",  # Modelo pequeño y rápido
                max_length=400,
                temperature=0.7,
                do_sample=True
            )
            return True
        except Exception as e:
            st.warning(f"⚠️ Modelo IA no disponible: {str(e)}")
            return False
    
    def generar_respuesta_ia(self, prompt, max_longitud=350):
        """Generar respuesta usando IA"""
        try:
            if not self.modelo_ia:
                return None
                
            respuesta = self.modelo_ia(
                prompt,
                max_new_tokens=max_longitud,
                pad_token_id=self.modelo_ia.tokenizer.eos_token_id
            )
            
            texto_generado = respuesta[0]['generated_text']
            # Limpiar y formatear la respuesta
            texto_generado = texto_generado.replace(prompt, "").strip()
            return texto_generado
            
        except Exception as e:
            st.error(f"❌ Error generando respuesta IA: {str(e)}")
            return None

# =========================================
# SISTEMA DE BÚSQUEDA SEMÁNTICA MEJORADO
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
            
            self.documentos = []
            self.nombres_docs = []
            
            for materia in os.listdir(base_path):
                materia_path = os.path.join(base_path, materia)
                if os.path.isdir(materia_path):
                    for archivo in os.listdir(materia_path):
                        if archivo.endswith('.txt'):
                            archivo_path = os.path.join(materia_path, archivo)
                            try:
                                with open(archivo_path, 'r', encoding='utf-8') as f:
                                    contenido = f.read()
                                    parrafos = self._dividir_en_parrafos(contenido)
                                    for i, parrafo in enumerate(parrafos):
                                        if len(parrafo.strip()) > 50:
                                            self.documentos.append(parrafo)
                                            self.nombres_docs.append(f"{materia}/{archivo} - Párrafo {i+1}")
                            except Exception:
                                continue
            
            if not self.documentos:
                return False
            
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
        parrafos = re.split(r'\n\s*\n|\.\s+[A-Z]', texto)
        return [p.strip() for p in parrafos if p.strip()]
    
    def buscar_similaridad(self, consulta, top_n=3):
        """Buscar los documentos más similares a la consulta"""
        if not self.documentos or self.vectorizer is None:
            return []
        
        try:
            consulta_tfidf = self.vectorizer.transform([consulta])
            similitudes = cosine_similarity(consulta_tfidf, self.matriz_tfidf).flatten()
            indices_similares = similitudes.argsort()[-top_n:][::-1]
            
            resultados = []
            for idx in indices_similares:
                if similitudes[idx] > 0.1:
                    resultados.append({
                        'contenido': self.documentos[idx],
                        'fuente': self.nombres_docs[idx],
                        'similitud': similitudes[idx]
                    })
            
            return resultados
            
        except Exception as e:
            return []

# =========================================
# GENERACIÓN DE RESPUESTAS HÍBRIDA (IA + BÚSQUEDA)
# =========================================
def generar_respuesta_avanzada(pregunta, materia, sistema_busqueda, sistema_ia):
    """Generar respuesta combinando IA y búsqueda semántica"""
    profesor = PROFESORES[materia]
    
    # Buscar contenido relevante
    resultados = sistema_busqueda.buscar_similaridad(pregunta)
    resultados_materia = [r for r in resultados if materia in r['fuente']]
    if not resultados_materia:
        resultados_materia = resultados
    
    # Construir contexto para IA
    contexto_ia = ""
    if resultados_materia:
        contexto_ia = "\n".join([
            f"Fuente: {r['fuente']}\nContenido: {r['contenido'][:300]}..."
            for r in resultados_materia[:2]
        ])
    
    # Crear prompt para IA
    prompt_ia = f"""
    Eres {profesor['nombre']}, un profesor especializado en {materia.replace('_', ' ')}.
    {profesor['personalidad']}
    
    CONTEXTO DEL MATERIAL:
    {contexto_ia}
    
    PREGUNTA DEL ESTUDIANTE:
    {pregunta}
    
    Responde como lo haría este profesor, usando el contexto proporcionado y tu expertise.
    Sé práctico, útil y mantén tu personalidad característica.
    Responde en español.
    
    RESPUESTA:
    """
    
    # Intentar generar con IA
    respuesta_ia = None
    if sistema_ia and sistema_ia.modelo_ia:
        respuesta_ia = sistema_ia.generar_respuesta_ia(prompt_ia)
    
    # Construir respuesta final
    if respuesta_ia:
        respuesta_final = f"""
        {profesor['emoji']} **{profesor['nombre']} responde:**
        
        {respuesta_ia}
        """
    else:
        # Fallback a respuesta semántica mejorada
        respuesta_final = generar_respuesta_semantica(pregunta, materia, resultados_materia, profesor)
    
    # Añadir referencias si hay resultados relevantes
    if resultados_materia:
        respuesta_final += f"\n\n**📚 Fuentes consultadas:**"
        for i, resultado in enumerate(resultados_materia[:2], 1):
            similitud_porcentaje = resultado['similitud'] * 100
            respuesta_final += f"\n• **{resultado['fuente']}** (relevancia: {similitud_porcentaje:.1f}%)"
    
    return respuesta_final

def generar_respuesta_semantica(pregunta, materia, resultados, profesor):
    """Generar respuesta usando solo búsqueda semántica"""
    respuesta = f"""
    {profesor['emoji']} **{profesor['nombre']} responde:**
    
    **Sobre tu pregunta:** "{pregunta}"
    """
    
    if resultados:
        respuesta += f"\n\n**📚 Basándome en el material, te recomiendo:**\n\n"
        for i, resultado in enumerate(resultados[:2], 1):
            respuesta += f"**{i}. {resultado['contenido'][:200]}...**\n"
            respuesta += f"   *Fuente: {resultado['fuente']}*\n\n"
    else:
        respuesta += f"\n\n**💡 {random.choice(profesor['consejos'])}**"
    
    respuesta += f"\n\n**🎯 Recuerda mi estilo:** {profesor['estilo']}"
    respuesta += f"\n\n**🌟 Consejo práctico:** {random.choice(profesor['consejos'])}"
    
    return respuesta

# =========================================
# INTERFAZ PRINCIPAL MEJORADA
# =========================================
def main():
    st.title("🎓 Asistente 4 Materias + IA Avanzada")
    st.markdown("### Ahora con generación inteligente de respuestas")
    
    # Inicializar sistemas
    if "sistema_busqueda" not in st.session_state:
        st.session_state.sistema_busqueda = SistemaBusqueda()
    
    if "sistema_ia" not in st.session_state:
        st.session_state.sistema_ia = SistemaIA()
    
    # Cargar sistemas
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner("🧠 Procesando conocimiento..."):
            if st.session_state.sistema_busqueda.cargar_y_procesar_conocimiento():
                st.success(f"✅ Búsqueda semántica - {len(st.session_state.sistema_busqueda.documentos)} párrafos")
    
    with col2:
        with st.spinner("🤖 Cargando IA..."):
            if st.session_state.sistema_ia.cargar_modelo_ligero():
                st.success("✅ Modelo IA cargado")
            else:
                st.info("🔧 IA no disponible - usando modo básico")
    
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
        
        # Selector de modo de respuesta
        st.markdown("---")
        st.subheader("⚡ Modo de Respuesta")
        modo_respuesta = st.radio(
            "Selecciona el modo:",
            ["Automático", "Solo Búsqueda", "Solo IA"],
            index=0,
            help="Automático: Combina IA y búsqueda. Solo Búsqueda: Más rápido. Solo IA: Más creativo."
        )
        
        st.markdown("---")
        st.markdown("**Consejos clave:**")
        for consejo in profesor['consejos'][:3]:
            st.write(f"• {consejo}")
        
        # Estadísticas del sistema
        st.markdown("---")
        st.subheader("🔍 Estado del Sistema")
        
        if st.session_state.sistema_busqueda.documentos:
            st.success(f"📊 {len(st.session_state.sistema_busqueda.documentos)} párrafos")
        else:
            st.warning("📝 Sin documentos")
        
        if st.session_state.sistema_ia.modelo_ia:
            st.success("🤖 IA disponible")
        else:
            st.warning("🤖 IA no disponible")
        
        st.markdown("---")
        
        if st.button("🔄 Reiniciar Sistemas", use_container_width=True):
            st.session_state.sistema_busqueda = SistemaBusqueda()
            st.session_state.sistema_ia = SistemaIA()
            st.rerun()
        
        if st.button("🧹 Limpiar Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"¡Hola! Soy {PROFESORES[selected_materia]['nombre']} {PROFESORES[selected_materia]['emoji']}. Ahora tengo capacidades de IA avanzada combinadas con búsqueda semántica. ¿En qué puedo ayudarte?"}
        ]
    
    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input(f"Pregunta sobre {selected_materia.replace('_', ' ')}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta según el modo seleccionado
        with st.chat_message("assistant"):
            with st.spinner(f"💭 {PROFESORES[selected_materia]['nombre']} piensa..."):
                if modo_respuesta == "Solo Búsqueda":
                    respuesta = generar_respuesta_semantica(
                        prompt, 
                        selected_materia, 
                        st.session_state.sistema_busqueda.buscar_similaridad(prompt),
                        PROFESORES[selected_materia]
                    )
                elif modo_respuesta == "Solo IA" and st.session_state.sistema_ia.modelo_ia:
                    respuesta = st.session_state.sistema_ia.generar_respuesta_ia(
                        f"Responde como {PROFESORES[selected_materia]['nombre']} a: {prompt}"
                    ) or "No pude generar una respuesta con IA en este momento."
                else:
                    respuesta = generar_respuesta_avanzada(
                        prompt, 
                        selected_materia, 
                        st.session_state.sistema_busqueda,
                        st.session_state.sistema_ia
                    )
                
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🤖 IA Avanzada**
        - Generación inteligente de respuestas
        - Personalidades de profesores
        - Contexto semántico
        """)
    
    with col2:
        st.success("""
        **🔍 Búsqueda Semántica**
        - TF-IDF + Cosine Similarity
        - 1000+ términos especializados
        - Resultados por relevancia
        """)
    
    with col3:
        st.warning("""
        **🎯 Próximas Mejoras**
        - Ejercicios interactivos
        - Evaluaciones automáticas
        - Análisis de progreso
        """)

if __name__ == "__main__":
    main()
