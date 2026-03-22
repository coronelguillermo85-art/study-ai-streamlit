import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import datetime
import os

st.set_page_config(page_title="Study AI", page_icon="🎓", layout="wide")

st.title("🎓 Study AI")
st.caption("Chat + PDF + OCR + Quiz + Diploma")

# =========================
# CONFIG API
# =========================
groq_key = st.text_input("Pegá tu Groq API Key", type="password")

# OPCIONAL: si Tesseract no se detecta solo en Windows,
# descomentá esta línea y ajustá la ruta.
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def consultar_llama(prompt):
    if not groq_key:
        st.error("Primero pegá tu API key de Groq.")
        return None

    try:
        client = Groq(api_key=groq_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.5
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error con Groq: {e}")
        return None

def extraer_texto_pdf(archivo_pdf):
    try:
        reader = PdfReader(archivo_pdf)
        texto_pdf = ""
        for page in reader.pages:
            texto_pagina = page.extract_text()
            if texto_pagina:
                texto_pdf += texto_pagina + "\n"
        return texto_pdf.strip()
    except Exception as e:
        st.error(f"Error leyendo PDF: {e}")
        return ""

def extraer_texto_imagen(archivo_imagen):
    try:
        imagen = Image.open(archivo_imagen)

        # OCR básico
        texto = pytesseract.image_to_string(imagen, lang="eng")

        # Si querés español y tenés el paquete instalado en Tesseract:
        # texto = pytesseract.image_to_string(imagen, lang="spa")

        return texto.strip()
    except Exception as e:
        st.error(f"Error en OCR: {e}")
        return ""

# =========================
# CHAT
# =========================
st.header("💬 Chat")
mensaje = st.text_input("Escribí tu mensaje")

if st.button("Enviar mensaje"):
    if mensaje.strip():
        respuesta = consultar_llama(mensaje)
        if respuesta:
            st.write("### Respuesta")
            st.write(respuesta)

st.divider()

# =========================
# PDF
# =========================
st.header("📄 Subir PDF")
archivo_pdf = st.file_uploader("Subí un PDF", type=["pdf"], key="pdf_uploader")

if archivo_pdf:
    texto_pdf = extraer_texto_pdf(archivo_pdf)
    if texto_pdf:
        st.session_state["texto_pdf"] = texto_pdf
        st.session_state["archivo_nombre"] = archivo_pdf.name
        st.success(f"PDF cargado: {archivo_pdf.name}")
    else:
        st.warning("No se pudo extraer texto del PDF.")

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
            st.write("### Resumen PDF")
            st.write(resumen)
    else:
        st.warning("Primero subí un PDF.")

st.divider()

# =========================
# OCR DE IMAGEN / FOTO
# =========================
st.header("📷 Subir foto o imagen con OCR")
archivo_imagen = st.file_uploader(
    "Subí una foto de apuntes, hoja o captura",
    type=["png", "jpg", "jpeg", "webp"],
    key="img_uploader"
)

if archivo_imagen:
    st.image(archivo_imagen, caption="Imagen subida", use_container_width=True)

    if st.button("Leer texto de la imagen (OCR)"):
        texto_ocr = extraer_texto_imagen(archivo_imagen)

        if texto_ocr:
            st.session_state["texto_ocr"] = texto_ocr
            st.success("Texto extraído con OCR.")
            st.write("### Texto detectado")
            st.text_area("Resultado OCR", texto_ocr, height=250)
        else:
            st.warning("No se pudo leer texto de la imagen.")

if st.button("Resumir texto de la imagen"):
    if "texto_ocr" in st.session_state and st.session_state["texto_ocr"].strip():
        prompt_ocr = f"""
Resumí este texto extraído de una imagen.
Luego agregá 3 puntos clave.

Texto:
{st.session_state["texto_ocr"][:4000]}
"""
        resumen_ocr = consultar_llama(prompt_ocr)
        if resumen_ocr:
            st.write("### Resumen de imagen")
            st.write(resumen_ocr)
    else:
        st.warning("Primero subí una imagen y ejecutá el OCR.")

st.divider()

# =========================
# QUIZ
# =========================
st.header("🧠 Quiz")

fuente_quiz = st.radio(
    "¿Sobre qué querés generar el quiz?",
    ["Tema general", "PDF cargado", "Texto OCR de imagen"],
    horizontal=True
)

if st.button("Generar quiz"):
    if fuente_quiz == "PDF cargado" and "texto_pdf" in st.session_state:
        prompt_quiz = f"""
Basado en este texto, generá 3 preguntas multiple choice con 4 opciones cada una.
Marcá también la respuesta correcta.

Texto:
{st.session_state["texto_pdf"][:3000]}
"""
    elif fuente_quiz == "Texto OCR de imagen" and "texto_ocr" in st.session_state:
        prompt_quiz = f"""
Basado en este texto extraído con OCR, generá 3 preguntas multiple choice con 4 opciones cada una.
Marcá también la respuesta correcta.

Texto:
{st.session_state["texto_ocr"][:3000]}
"""
    else:
        prompt_quiz = """
Generá 3 preguntas multiple choice con 4 opciones cada una sobre un tema general de estudio.
Marcá también la respuesta correcta.
"""

    quiz = consultar_llama(prompt_quiz)
    if quiz:
        st.write("### Quiz")
        st.write(quiz)

st.divider()

# =========================
# EVALUACIÓN Y DIPLOMA
# =========================
st.header("🎓 Evaluación y diploma")
respuesta_usuario = st.text_area("Explicá qué aprendiste o respondé una consigna")

contexto_eval = st.radio(
    "Contexto para evaluar",
    ["Sin contexto", "Usar PDF", "Usar OCR de imagen"],
    horizontal=True
)

if st.button("Evaluar y dar diploma"):
    if respuesta_usuario.strip():
        contexto = ""
        tema = "Estudio General"

        if contexto_eval == "Usar PDF" and "texto_pdf" in st.session_state:
            contexto = st.session_state["texto_pdf"][:1500]
            tema = st.session_state.get("archivo_nombre", "PDF").replace(".pdf", "")
        elif contexto_eval == "Usar OCR de imagen" and "texto_ocr" in st.session_state:
            contexto = st.session_state["texto_ocr"][:1500]
            tema = "Texto extraído de imagen"

        prompt_eval = f"""
Contexto del material:
{contexto}

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
