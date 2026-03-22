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
# ESTILOS
# =========================
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1100px;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81);
        color: white;
        padding: 1.2rem;
        border-radius: 22px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.16);
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
        line-height: 1.1;
    }

    .hero p {
        margin-top: 0.5rem;
        margin-bottom: 0;
        opacity: 0.95;
        font-size: 1rem;
    }

    .chip {
        display: inline-block;
        background: #eef2ff;
        color: #3730a3;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #111827;
    }

    .small-note {
        color: #6b7280;
        font-size: 0.93rem;
    }

    .chat-user {
        background: #eef2ff;
        border-radius: 16px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
    }

    .chat-ai {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0 1rem 0;
    }

    .diploma-box {
        border: 4px solid #4338ca;
        border-radius: 20px;
        padding: 28px;
        background: linear-gradient(180deg, #ffffff, #eef2ff);
        margin-top: 1rem;
        box-shadow: 0 10px 30px rgba(67, 56, 202, 0.12);
    }

    .diploma-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        color: #312e81;
        margin-bottom: 0.2rem;
    }

    .diploma-sub {
        text-align: center;
        color: #374151;
        margin-bottom: 1rem;
    }

    @media (max-width: 768px) {
        .hero h1 {
            font-size: 1.6rem;
        }

        .hero p {
            font-size: 0.95rem;
        }

        .diploma-title {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="hero">
    <h1>🎓 Sensitive Study</h1>
    <p>
        Tu espacio de estudio con IA: chat, resúmenes, OCR, quizzes y diploma.
        Funciona con tu propia API de Groq.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<span class="chip">💬 Chat IA</span>
<span class="chip">📄 PDF</span>
<span class="chip">📷 OCR</span>
<span class="chip">🧠 Quiz</span>
<span class="chip">⚡ Modo rápido</span>
<span class="chip">🎓 Diploma</span>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = ""

if "texto_ocr" not in st.session_state:
    st.session_state.texto_ocr = ""

if "archivo_nombre" not in st.session_state:
    st.session_state.archivo_nombre = "Estudio General"

if "chat_input_prefill" not in st.session_state:
    st.session_state.chat_input_prefill = ""

# Si en local Tesseract no se detecta, descomentá esta línea:
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# =========================
# API
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🔐 Activación</div>', unsafe_allow_html=True)
st.write("Pegá tu API de Groq. Cada usuario usa su propia IA.")

groq_key = st.text_input(
    "Groq API Key",
    type="password",
    placeholder="Pegá acá tu key"
)

st.markdown(
    '<div class="small-note">Tu clave no se guarda en esta versión. Cada usuario usa su propia API.</div>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

def cliente_groq():
    if not groq_key:
        st.error("Primero pegá tu API key de Groq.")
        return None
    try:
        return Groq(api_key=groq_key)
    except Exception as e:
        st.error(f"Error creando cliente Groq: {e}")
        return None

def preguntar_groq(messages, model="llama-3.1-8b-instant"):
    client = cliente_groq()
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error con Groq: {e}")
        return None

def extraer_texto_pdf(archivo_pdf):
    try:
        reader = PdfReader(archivo_pdf)
        texto = ""
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                texto += txt + "\n"
        return texto.strip()
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
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Chat",
    "📄 PDF",
    "📷 OCR",
    "🧠 Quiz",
    "⚡ Modo rápido",
    "🎓 Diploma"
])

# =========================
# CHAT
# =========================
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Chat de estudio</div>', unsafe_allow_html=True)
    st.caption("Ahora el chat guarda contexto y responde mejor.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Explicame este tema", use_container_width=True):
            st.session_state.chat_input_prefill = "Explicame este tema de forma clara, con ejemplo y puntos clave."

    with col2:
        if st.button("Haceme preguntas", use_container_width=True):
            st.session_state.chat_input_prefill = "Haceme 5 preguntas para comprobar si entendí este tema."

    with col3:
        if st.button("Tomame mini examen", use_container_width=True):
            st.session_state.chat_input_prefill = "Tomame un mini examen de 3 preguntas sobre este tema."

    mensaje = st.text_area(
        "Escribí tu mensaje",
        value=st.session_state.chat_input_prefill,
        placeholder="Ejemplo: explicame este tema paso a paso y después haceme preguntas.",
        height=120,
        key="chat_box"
    )

    a, b = st.columns([3, 1])
    with a:
        enviar = st.button("Enviar mensaje", use_container_width=True)
    with b:
        limpiar = st.button("Limpiar chat", use_container_width=True)

    if limpiar:
        st.session_state.chat_history = []
        st.session_state.chat_input_prefill = ""
        st.rerun()

    if enviar:
        if mensaje.strip():
            system_prompt = """
Sos Sensitive Study, un tutor académico en español.
Respondé de
