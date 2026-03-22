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

# Si Tesseract no se detecta, descomentá esto en local:
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

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


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Chat",
    "📄 PDF",
    "📷 OCR",
    "🧠 Quiz",
    "⚡ Modo rápido",
    "🎓 Diploma"
])

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
Respondé de forma clara, útil y completa.
No respondas demasiado corto.
Usá ejemplos si ayudan.
Si corresponde, cerrá con 2 o 3 preguntas de repaso.
"""

            messages = [{"role": "system", "content": system_prompt}]

            for item in st.session_state.chat_history:
                messages.append(item)

            contexto = ""
            if st.session_state.texto_pdf:
                contexto += f"\n\nContexto del PDF:\n{st.session_state.texto_pdf[:2500]}"
            if st.session_state.texto_ocr:
                contexto += f"\n\nContexto del OCR:\n{st.session_state.texto_ocr[:2500]}"

            contenido_usuario = mensaje + contexto
            messages.append({"role": "user", "content": contenido_usuario})

            respuesta = preguntar_groq(messages)

            if respuesta:
                st.session_state.chat_history.append({"role": "user", "content": mensaje})
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
                st.session_state.chat_input_prefill = ""
                st.rerun()
        else:
            st.warning("Escribí algo primero.")

    if st.session_state.chat_history:
        st.markdown("#### Conversación")
        for item in st.session_state.chat_history:
            if item["role"] == "user":
                st.markdown(
                    f'<div class="chat-user"><strong>Vos:</strong><br>{item["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-ai"><strong>Sensitive Study:</strong><br>{item["content"]}</div>',
                    unsafe_allow_html=True
                )

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Subir PDF</div>', unsafe_allow_html=True)
    st.caption("Subí apuntes o material de estudio y generá un resumen mejor.")

    archivo_pdf = st.file_uploader("Elegí un PDF", type=["pdf"], key="pdf_uploader")

    if archivo_pdf:
        texto_pdf = extraer_texto_pdf(archivo_pdf)
        if texto_pdf:
            st.session_state.texto_pdf = texto_pdf
            st.session_state.archivo_nombre = archivo_pdf.name
            st.success(f"PDF cargado: {archivo_pdf.name}")
        else:
            st.warning("No se pudo extraer texto del PDF.")

    col_pdf_1, col_pdf_2 = st.columns(2)

    with col_pdf_1:
        if st.button("Generar resumen del PDF", use_container_width=True):
            if st.session_state.texto_pdf:
                messages = [
                    {
                        "role": "system",
                        "content": """Sos un tutor académico.
Hacé resúmenes útiles para estudiar.
Tu salida debe incluir:
1. Resumen general
2. 5 puntos clave
3. 3 conceptos difíciles explicados simple
4. 5 preguntas de repaso"""
                    },
                    {
                        "role": "user",
                        "content": f"Resumí este material:\n\n{st.session_state.texto_pdf[:12000]}"
                    }
                ]
                resumen = preguntar_groq(messages)
                if resumen:
                    st.markdown("#### Resumen")
                    st.write(resumen)
            else:
                st.warning("Primero subí un PDF.")

    with col_pdf_2:
        if st.button("Preguntarme sobre este PDF", use_container_width=True):
            if st.session_state.texto_pdf:
                st.session_state.chat_input_prefill = "Haceme preguntas sobre el PDF que subí para comprobar si lo entendí."
                st.success("Ahora andá a la pestaña Chat.")
            else:
                st.warning("Primero subí un PDF.")

    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Foto / OCR</div>', unsafe_allow_html=True)
    st.caption("Subí una foto de apuntes o captura y extraé el texto.")

    archivo_imagen = st.file_uploader(
        "Subí una imagen",
        type=["png", "jpg", "jpeg", "webp"],
        key="img_uploader"
    )

    if archivo_imagen:
        st.image(archivo_imagen, caption="Imagen cargada", use_container_width=True)

        col_ocr_1, col_ocr_2 = st.columns(2)

        with col_ocr_1:
            if st.button("Leer texto de la imagen", use_container_width=True):
                texto_ocr = extraer_texto_imagen(archivo_imagen)
                if texto_ocr:
                    st.session_state.texto_ocr = texto_ocr
                    st.success("Texto detectado con OCR.")
                    st.text_area("Texto extraído", texto_ocr, height=220)
                else:
                    st.warning("No se pudo leer texto de la imagen.")

        with col_ocr_2:
            if st.button("Explicar texto extraído", use_container_width=True):
                if st.session_state.texto_ocr.strip():
                    messages = [
                        {
                            "role": "system",
                            "content": "Sos un tutor. Explicá en español, con claridad, usando ejemplos y puntos clave."
                        },
                        {
                            "role": "user",
                            "content": f"Explicá este texto extraído por OCR:\n\n{st.session_state.texto_ocr[:8000]}"
                        }
                    ]
                    explicacion = preguntar_groq(messages)
                    if explicacion:
                        st.markdown("#### Explicación")
                        st.write(explicacion)
                else:
                    st.warning("Primero ejecutá el OCR.")

    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Quiz</div>', unsafe_allow_html=True)

    fuente_quiz = st.radio(
        "Fuente del quiz",
        ["Tema general", "PDF cargado", "Texto OCR"],
        horizontal=True
    )

    tema_manual = st.text_input("Tema opcional", placeholder="Ejemplo: historia, biología, relaciones públicas...")

    if st.button("Generar quiz", use_container_width=True):
        if fuente_quiz == "PDF cargado" and st.session_state.texto_pdf:
            base = st.session_state.texto_pdf[:8000]
            prompt = f"Generá 5 preguntas multiple choice con 4 opciones, marcá la correcta y explicá brevemente. Basate en:\n\n{base}"
        elif fuente_quiz == "Texto OCR" and st.session_state.texto_ocr:
            base = st.session_state.texto_ocr[:8000]
            prompt = f"Generá 5 preguntas multiple choice con 4 opciones, marcá la correcta y explicá brevemente. Basate en:\n\n{base}"
        else:
            prompt = f"Generá 5 preguntas multiple choice con 4 opciones sobre este tema: {tema_manual or 'tema general de estudio'}. Marcá la correcta y explicá brevemente."

        messages = [
            {"role": "system", "content": "Sos un generador de quizzes didácticos en español."},
            {"role": "user", "content": prompt}
        ]
        quiz = preguntar_groq(messages)
        if quiz:
            st.markdown("#### Quiz")
            st.write(quiz)

    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Modo rápido</div>', unsafe_allow_html=True)

    tema_rapido = st.text_input(
        "Tema a estudiar",
        placeholder="Ejemplo: comunicación institucional, sistema digestivo, romanticismo..."
    )

    if st.button("Generar guía rápida", use_container_width=True):
        if tema_rapido.strip():
            messages = [
                {
                    "role": "system",
                    "content": """Sos un tutor académico.
Armá guías rápidas para estudiar con:
1. Explicación simple
2. Puntos clave
3. Ejemplo
4. 3 preguntas de repaso"""
                },
                {
                    "role": "user",
                    "content": f"Quiero estudiar este tema: {tema_rapido}"
                }
            ]
            guia = preguntar_groq(messages)
            if guia:
                st.markdown("#### Guía rápida")
                st.write(guia)
        else:
            st.warning("Escribí un tema primero.")

    st.markdown('</div>', unsafe_allow_html=True)

with tab6:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Evaluación y diploma</div>', unsafe_allow_html=True)

    contexto_eval = st.radio(
        "Contexto",
        ["Sin contexto", "Usar PDF", "Usar OCR"],
        horizontal=True
    )

    respuesta_usuario = st.text_area(
        "Tu respuesta",
        placeholder="Respondé una consigna o explicá lo que aprendiste.",
        height=180
    )

    if st.button("Evaluar y emitir diploma", use_container_width=True):
        if respuesta_usuario.strip():
            contexto = ""
            tema_diploma = "Estudio General"

            if contexto_eval == "Usar PDF" and st.session_state.texto_pdf:
                contexto = st.session_state.texto_pdf[:2500]
                tema_diploma = st.session_state.archivo_nombre.replace(".pdf", "")
            elif contexto_eval == "Usar OCR" and st.session_state.texto_ocr:
                contexto = st.session_state.texto_ocr[:2500]
                tema_diploma = "Texto extraído por OCR"

            messages = [
                {
                    "role": "system",
                    "content": "Sos un evaluador académico. Respondé SOLO con APROBADO o REPROBADO."
                },
                {
                    "role": "user",
                    "content": f"Contexto:\n{contexto}\n\nRespuesta del alumno:\n{respuesta_usuario}"
                }
            ]
            resultado = preguntar_groq(messages)

            if resultado and "APROBADO" in resultado.upper():
                st.success("¡Aprobado!")
                st.balloons()

                st.markdown(f"""
                <div class="diploma-box">
                    <div class="diploma-title">CERTIFICADO DE LOGRO</div>
                    <div class="diploma-sub">Sensitive Study</div>
                    <p style="text-align:center; font-size:18px;">
                        Se certifica dominio satisfactorio en:
                    </p>
                    <h2 style="text-align:center;">{tema_diploma}</h2>
                    <p style="text-align:center; margin-top:18px;">
                        Validado con IA • Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("La evaluación fue reprobada. Probá de nuevo.")
        else:
            st.warning("Escribí una respuesta primero.")

    st.markdown('</div>', unsafe_allow_html=True)
