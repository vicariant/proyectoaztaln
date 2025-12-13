import os
import requests
import random
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Configuración de Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# --- MODELO NUEVO (ACTUALIZADO) ---
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index():
    return render_template("explorador.html")

# --- API 1: CHAT ORÁCULO ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        user_query = data.get('user_query')
        lang = data.get('lang', 'es')
        
        role_msg = "Eres la IA del sistema AZTLAN OS. Responde de forma técnica."
        if lang == 'en': role_msg += " RESPONDE EN INGLÉS."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})

    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}")
        return jsonify({"answer": f"⚠️ ERROR DE SISTEMA: {error_msg}"})

# --- API 2: PREDICCIÓN ML ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict():
    try:
        data = request.json
        lang = data.get('lang', 'es')
        prompt = f"Analiza exoplaneta: Radio={data.get('koi_prad')}, Temp={data.get('koi_steff')}. Responde JSON: prediccion, probabilidad, analisis_tecnico. Idioma: {lang}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODELO_IA, temperature=0.5,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return jsonify({"prediccion": "ERROR", "probabilidad": "0%", "analisis_tecnico": f"Fallo: {str(e)}"})

# --- API 3: REPORTE CIENTÍFICO ---
@app.route("/api/aztlan-deep", methods=["POST"])
def deep_scan():
    try:
        data = request.json
        prompt = f"Reporte corto sobre {data.get('planet_name')}."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=MODELO_IA,
        )
        return jsonify({"report": chat_completion.choices[0].message.content})
    except:
        return jsonify({"report": "Sin datos."})

# --- API 4: GALERÍA NASA ---
@app.route("/api/nasa-feed")
def nasa_feed():
    try:
        query = request.args.get('q', 'galaxy')
        url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"
        r = requests.get(url).json()
        items = r['collection']['items'][:8]
        images = [{"url": item['links'][0]['href'], "title": item['data'][0]['title']} for item in items if 'links' in item]
        return jsonify(images)
    except:
        return jsonify([])

# --- API 5: JUEGO ---
@app.route("/api/game-analysis", methods=["POST"])
def game_analysis():
    try:
        data = request.json
        prompt = f"Jugador obtuvo {data.get('score')} puntos. Comentario breve militar."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=MODELO_IA, max_tokens=60
        )
        return jsonify({"comment": chat_completion.choices[0].message.content})
    except:
        return jsonify({"comment": "Fin de simulación."})

if __name__ == "__main__":
    app.run(debug=True)
