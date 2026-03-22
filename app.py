import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import datetime

st.set_page_config(page_title="Study AI", page_icon="🎓", layout="wide")

st.title("🎓 Study AI")
st.caption("Chat + PDF + Quiz + Diploma")

# --- API KEY ---
groq_key = st.text_input("Pegá tu Groq API Key", type="password")

def consultar_llama(prompt):
    if not groq_key:
        st.error("Primero pegá tu API key de Groq.")
        return None

    try:
        client = Groq(api_key=groq_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.5
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error con Groq: {e}")
        return None

# --- CHAT TIPO GPT ---
st.header("💬 Chat")
mensaje = st.text_input("Escribí tu mensaje")

if st.button("Enviar mensaje"):
    if mensaje.strip():
        respuesta = consultar_llama(mensaje)
        if respuesta:
            st.write("### Respuesta")
            st.write(respuesta)

st.divider()

# --- PDF ---
st.header("📄 Subir PDF")
archivo = st.file_uploader("Subí un PDF", type=["pdf"])

if archivo:
    try:
        reader = PdfReader(archivo)
        texto_pdf = ""

        for page in reader.pages:
            texto_pagina = page.extract_text()
            if texto_pagina:
                texto_pdf += texto_pagina

        if texto_pdf.strip():
            st.session_state["texto_pdf"] = texto_pdf
            st.session_state["archivo_nombre"] = archivo.name
            st.success(f"PDF cargado: {archivo.name}")
        else:
            st.warning("No se pudo extraer texto del PDF.")
    except Exception as e:
        st.error(f"Error leyendo PDF: {e}")

if st.button("Generar resumen del PDF"):
    if "texto_pdf" in st.session_state:
        prompt_resumen = f"""
Resumí este documento de forma clara.
Después agregá 3 puntos clave.

Documento:
{st.session_state["texto_pdf"][:4000]}
"""
        resumen = consultar_llama(prompt_resumen)
        if resumen:
            st.write("### Resumen")
            st.write(resumen)
    else:
        st.warning("Primero subí un PDF.")

st.divider()

# --- QUIZ ---
st.header("🧠 Quiz")

if st.button("Generar quiz"):
    if "texto_pdf" in st.session_state:
        prompt_quiz = f"""
Basado en este texto, generá 3 preguntas multiple choice con 4 opciones cada una.

Texto:
{st.session_state["texto_pdf"][:3000]}
"""
    else:
        prompt_quiz = "Generá 3 preguntas multiple choice con 4 opciones cada una sobre un tema general de estudio."

    quiz = consultar_llama(prompt_quiz)
    if quiz:
        st.write("### Quiz")
        st.write(quiz)

st.divider()

# --- EVALUACIÓN Y DIPLOMA ---
st.header("🎓 Evaluación y diploma")
respuesta_usuario = st.text_area("Explicá qué aprendiste o respondé una consigna")

if st.button("Evaluar y dar diploma"):
    if respuesta_usuario.strip():
        contexto = st.session_state.get("texto_pdf", "")
        prompt_eval = f"""
Contexto del material:
{contexto[:1500]}

Respuesta del alumno:
{respuesta_usuario}

Respondé SOLO una palabra:
APROBADO
o
REPROBADO
"""
        resultado = consultar_llama(prompt_eval)

        if resultado and "APROBADO" in resultado.upper():
            st.success("¡Aprobado!")
            st.balloons()

            tema = st.session_state.get("archivo_nombre", "Estudio General").replace(".pdf", "")

            st.markdown(f"""
<div style="border: 4px solid #6c63ff; padding: 30px; border-radius: 16px; background: #f9f9ff;">
    <h1 style="text-align:center; color:#6c63ff;">CERTIFICADO DE LOGRO</h1>
    <p style="text-align:center; font-size:18px;">Se certifica que completaste satisfactoriamente:</p>
    <h2 style="text-align:center;">{tema}</h2>
    <p style="text-align:center;">Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}</p>
</div>
""", unsafe_allow_html=True)
        else:
            st.error("La evaluación fue reprobada. Probá de nuevo.")
    else:
        st.warning("Escribí una respuesta primero.")