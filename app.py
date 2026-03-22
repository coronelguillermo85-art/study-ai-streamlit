import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import datetime

st.set_page_config(
    page_title="Sensitive Study",
    page_icon="🎓",
    layout="wide"
)

# =========================
# ESTILOS RESPONSIVE / MOBILE
# =========================
st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1100px;
    }

    .hero-box {
        background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81);
        padding: 1.3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.18);
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        line-height: 1.1;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        margin-bottom: 0;
    }

    .info-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    }

    .mini-badge {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: #eef2ff;
        color: #4338ca;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
        color: #111827;
    }

    .diploma-box {
        border: 4px solid #4f46e5;
        padding: 28px;
        border-radius: 20px;
        background: linear-gradient(180deg, #ffffff, #eef2ff);
        color: #1f2937;
        margin-top: 1rem;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.10);
    }

    .diploma-title {
        text-align: center;
        color: #312e81;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 0.3rem;
    }

    .diploma-sub {
        text-align: center;
        font-size: 1rem;
        margin-bottom: 1rem;
        color: #374151;
    }

    .small-note {
        font-size: 0.92rem;
        color: #6b7280;
    }

    .feature-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.8rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .hero-title {
            font-size: 1.6rem;
        }

        .hero-subtitle {
            font-size: 0.95rem;
        }

        .diploma-title {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CABECERA
# =========================
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🎓 Sensitive Study</div>
    <p class="hero-subtitle">
        Tu espacio de estudio con IA: chat, resúmenes, OCR, quizzes y diploma.
        Funciona con tu propia API de Groq.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-grid">
    <span class="mini-badge">💬 Chat IA</span>
    <span class="mini-badge">📄 PDF</span>
    <span class="mini-badge">📷 OCR</span>
    <span class="mini-badge">🧠 Quiz</span>
    <span class="mini-badge">⚡ Modo rápido</span>
    <span class="mini-badge">🎓 Diploma</span>
</div>
""", unsafe_allow_html=True)

# =========================
# CONFIG API
# =========================
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown("### 🔐 Activación")
st.caption("Pegá tu propia API de Groq para usar tu IA. Así cada usuario controla su consumo.")

groq_key = st.text_input("Groq API Key", type="password", placeholder="Pegá acá tu key de Groq")

st.markdown(
    '<p class="small-note">Tu clave no se guarda en esta versión. Cada usuario usa su propia API.</p>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# Si Tesseract no se detecta en tu compu local, descomentá esta línea y ajustá la ruta:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def consultar_llama(prompt: str):
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
        texto = pytesseract.image_to_string(imagen, lang="eng")
        return texto.strip()
    except Exception as e:
        st.error(f"Error en OCR: {e}")
        return ""

# =========================
# TABS PRINCIPALES
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Chat",
    "📄 PDF",
    "📷 OCR",
    "🧠 Quiz",
    "⚡ Estudio rápido",
    "🎓 Diploma"
])

# =========================
# TAB CHAT
# =========================
with tab1:
    st.markdown('<div class="section-title">Chat con tu IA</div>', unsafe_allow_html=True)
    st.caption("Usalo como un mini ChatGPT para estudiar, repasar o pedir explicaciones.")

    mensaje = st.text_area(
        "Escribí tu mensaje",
        placeholder="Ejemplo: Explicame qué es la teoría de sistemas en lenguaje simple.",
        height=140
    )

    if st.button("Enviar mensaje", use_container_width=True):
        if mensaje.strip():
            respuesta = consultar_llama(mensaje)
            if respuesta:
                st.markdown("#### Respuesta")
                st.write(respuesta)
        else:
            st.warning("Escribí algo primero.")

# =========================
# TAB PDF
# =========================
with tab2:
    st.markdown('<div class="section-title">Subir PDF</div>', unsafe_allow_html=True)
    st.caption("Subí apuntes o material de estudio y generá un resumen claro.")

    archivo_pdf = st.file_uploader(
        "Elegí un PDF",
        type=["pdf"],
        key="pdf_uploader"
    )

    if archivo_pdf:
        texto_pdf = extraer_texto_pdf(archivo_pdf)
        if texto_pdf:
            st.session_state["texto_pdf"] = texto_pdf
            st.session_state["archivo_nombre"] = archivo_pdf.name
            st.success(f"PDF cargado: {archivo_pdf.name}")
        else:
            st.warning("No se pudo extraer texto del PDF.")

    if st.button("Generar resumen del PDF", use_container_width=True):
        if "texto_pdf" in st.session_state:
            prompt_resumen = f"""
Actuá como tutor.
Resumí este documento de forma clara y ordenada.
Después agregá 3 puntos clave.
Usá un tono útil para estudiar.

Documento:
{st.session_state["texto_pdf"][:4000]}
"""
            resumen = consultar_llama(prompt_resumen)
            if resumen:
                st.markdown("#### Resumen del PDF")
                st.write(resumen)
        else:
            st.warning("Primero subí un PDF.")

# =========================
# TAB OCR
# =========================
with tab3:
    st.markdown('<div class="section-title">Foto / OCR</div>', unsafe_allow_html=True)
    st.caption("Ideal para usar desde el celu con una foto de apuntes, hojas o capturas.")

    archivo_imagen = st.file_uploader(
        "Subí una foto o imagen",
        type=["png", "jpg", "jpeg", "webp"],
        key="img_uploader"
    )

    if archivo_imagen:
        st.image(archivo_imagen, caption="Imagen cargada", use_container_width=True)

        if st.button("Leer texto de la imagen", use_container_width=True):
            texto_ocr = extraer_texto_imagen(archivo_imagen)

            if texto_ocr:
                st.session_state["texto_ocr"] = texto_ocr
                st.success("Texto extraído con OCR.")
                st.text_area("Texto detectado", texto_ocr, height=220)
            else:
                st.warning("No se pudo leer texto de la imagen.")

    if st.button("Resumir texto de la imagen", use_container_width=True):
        if "texto_ocr" in st.session_state and st.session_state["texto_ocr"].strip():
            prompt_ocr = f"""
Resumí este texto extraído de una imagen.
Luego agregá 3 ideas principales y una mini explicación simple.

Texto:
{st.session_state["texto_ocr"][:4000]}
"""
            resumen_ocr = consultar_llama(prompt_ocr)
            if resumen_ocr:
                st.markdown("#### Resumen del OCR")
                st.write(resumen_ocr)
        else:
            st.warning("Primero subí una imagen y ejecutá el OCR.")

# =========================
# TAB QUIZ
# =========================
with tab4:
    st.markdown('<div class="section-title">Generador de quiz</div>', unsafe_allow_html=True)
    st.caption("Podés generar preguntas desde un PDF, una foto o un tema general.")

    fuente_quiz = st.radio(
        "Fuente del quiz",
        ["Tema general", "PDF cargado", "Texto OCR de imagen"],
        horizontal=True
    )

    if st.button("Generar quiz", use_container_width=True):
        if fuente_quiz == "PDF cargado" and "texto_pdf" in st.session_state:
            prompt_quiz = f"""
Basado en este texto, generá 5 preguntas multiple choice con 4 opciones cada una.
Marcá claramente la respuesta correcta.
Al final agregá una mini explicación por pregunta.

Texto:
{st.session_state["texto_pdf"][:3000]}
"""
        elif fuente_quiz == "Texto OCR de imagen" and "texto_ocr" in st.session_state:
            prompt_quiz = f"""
Basado en este texto extraído con OCR, generá 5 preguntas multiple choice con 4 opciones cada una.
Marcá claramente la respuesta correcta.
Al final agregá una mini explicación por pregunta.

Texto:
{st.session_state["texto_ocr"][:3000]}
"""
        else:
            prompt_quiz = """
Generá 5 preguntas multiple choice con 4 opciones cada una sobre un tema general de estudio.
Marcá claramente la respuesta correcta y agregá una mini explicación por pregunta.
"""

        quiz = consultar_llama(prompt_quiz)
        if quiz:
            st.markdown("#### Quiz")
            st.write(quiz)

# =========================
# TAB ESTUDIO RÁPIDO
# =========================
with tab5:
    st.markdown('<div class="section-title">Modo estudio rápido</div>', unsafe_allow_html=True)
    st.caption("Elegí un tema y recibí resumen, conceptos clave y una mini guía para repasar.")

    tema_rapido = st.text_input(
        "Tema a estudiar",
        placeholder="Ejemplo: Relaciones públicas, anatomía, derecho administrativo, CSS..."
    )

    if st.button("Activar modo estudio rápido", use_container_width=True):
        if tema_rapido.strip():
            prompt_rapido = f"""
Quiero estudiar este tema: {tema_rapido}

Armá una respuesta con esta estructura:
1. Explicación simple
2. 5 conceptos clave
3. 3 preguntas para autoevaluarme
4. Un mini consejo para memorizarlo mejor

Usá un tono claro, didáctico y útil.
"""
            resultado_rapido = consultar_llama(prompt_rapido)
            if resultado_rapido:
                st.markdown("#### Guía rápida")
                st.write(resultado_rapido)
        else:
            st.warning("Escribí un tema primero.")

# =========================
# TAB DIPLOMA
# =========================
with tab6:
    st.markdown('<div class="section-title">Evaluación y diploma</div>', unsafe_allow_html=True)
    st.caption("Respondé una consigna y la IA decide si aprobás.")

    contexto_eval = st.radio(
        "Contexto para evaluar",
        ["Sin contexto", "Usar PDF", "Usar OCR de imagen"],
        horizontal=True
    )

    respuesta_usuario = st.text_area(
        "Escribí tu respuesta",
        placeholder="Explicá lo que aprendiste o respondé una consigna.",
        height=180
    )

    if st.button("Evaluar y emitir diploma", use_container_width=True):
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
Actuá como evaluador académico.

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
                <div class="diploma-box">
                    <div class="diploma-title">CERTIFICADO DE LOGRO</div>
                    <div class="diploma-sub">Sensitive Study</div>
                    <p style="text-align:center; font-size: 18px;">
                        Se certifica que completaste satisfactoriamente:
                    </p>
                    <h2 style="text-align:center; margin-top: 8px;">{tema}</h2>
                    <p style="text-align:center; margin-top: 20px;">
                        Validado con IA • Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("La evaluación fue reprobada. Probá de nuevo.")
        else:
            st.warning("Escribí una respuesta primero.")
