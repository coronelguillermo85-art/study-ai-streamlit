from http.server import BaseHTTPRequestHandler
import json
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        tipo = data.get("tipo", "chat")

        # 🧠 CHAT NORMAL
        if tipo == "chat":
            mensaje = data.get("mensaje", "")

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": mensaje}],
                model="llama3-8b-8192"
            )

            respuesta = res.choices[0].message.content

            self._send({"respuesta": respuesta})
            return

        # 📚 RESUMEN PDF
        if tipo == "resumen":
            texto = data.get("texto", "")

            prompt = f"Resumí esto en puntos claros:\n{texto[:3000]}"

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )

            resultado = res.choices[0].message.content

            self._send({"resultado": resultado})
            return

        # 🧠 QUIZ
        if tipo == "quiz":
            prompt = "Generá 3 preguntas tipo multiple choice con 4 opciones."

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )

            quiz = res.choices[0].message.content

            self._send({"quiz": quiz})
            return

        # 🎓 EVALUACIÓN
        if tipo == "evaluar":
            respuesta_user = data.get("respuesta", "")

            prompt = f"""
Evaluá esta respuesta.

Respondé SOLO: APROBADO o REPROBADO.

Respuesta:
{respuesta_user}
"""

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )

            resultado = res.choices[0].message.content

            self._send({"resultado": resultado})
            return

    def _send(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())