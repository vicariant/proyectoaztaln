import os
import requests
import random
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Configuración de Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.route("/")
def index():
    # Carga tu archivo con el diseño v6.0
    return render_template("explorador.html")

# --- API 1: CHAT ORÁCULO ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    data = request.json
    user_query = data.get('user_query')
    system_msg = "Eres la IA del sistema AZTLAN OS v6. Responde de forma técnica, breve y futurista."
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_query}],
            model="llama3-8b-8192", temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
    except:
        return jsonify({"answer": "Error de enlace satelital."})

# --- API 2: PREDICCIÓN EXOPLANETAS ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict():
    data = request.json
    try:
        # Simulación de análisis basada en los datos
        score = float(data.get('koi_prad', 1))
        es_planeta = score < 2.5 # Si es pequeño, probablemente sea rocoso/confirmado
        
        return jsonify({
            "prediccion": "CANDIDATO CONFIRMADO" if es_planeta else "FALSO POSITIVO",
            "probabilidad": f"{random.randint(88, 99)}.{random.randint(1,9)}%",
            "analisis_tecnico": f"Radio planetario de {score} R⊕ detectado. {'Dentro' if es_planeta else 'Fuera'} de parámetros habitables."
        })
    except:
        return jsonify({"prediccion": "ERROR", "probabilidad": "0%", "analisis_tecnico": "Fallo en sensores."})

# --- API 3: REPORTE CIENTÍFICO ---
@app.route("/api/aztlan-deep", methods=["POST"])
def deep_scan():
    data = request.json
    prompt = f"Genera un reporte científico breve (formato Markdown) sobre el exoplaneta {data.get('planet_name')}."
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192",
        )
        return jsonify({"report": chat_completion.choices[0].message.content})
    except:
        return jsonify({"report": "Datos insuficientes."})

# --- API 4: GALERÍA NASA ---
@app.route("/api/nasa-feed")
def nasa_feed():
    query = request.args.get('q', 'galaxy')
    try:
        # Aquí usamos 'requests', por eso es vital ponerlo en requirements.txt
        url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"
        r = requests.get(url).json()
        items = r['collection']['items'][:8]
        images = [{"url": item['links'][0]['href'], "title": item['data'][0]['title']} for item in items if 'links' in item]
        return jsonify(images)
    except:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
