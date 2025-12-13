import os
import requests
import random
import json # Agregamos json por si acaso
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Configuración de Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.route("/")
def index():
    return render_template("explorador.html")

# --- API 1: CHAT ORÁCULO (CON DETECTOR DE ERRORES) ---
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
            model="llama3-8b-8192", temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})

    except Exception as e:
        # AQUÍ ESTÁ EL DETECTIVE DE ERRORES
        error_msg = str(e)
        print(f"ERROR CRÍTICO EN HEROKU: {error_msg}") # Esto sale en los logs
        
        if "401" in error_msg:
            return jsonify({"answer": "⚠️ ERROR 401: La llave API es incorrecta. Revisa 'Config Vars' en Heroku."})
        elif "404" in error_msg:
            return jsonify({"answer": "⚠️ ERROR 404: El modelo de IA no responde."})
        else:
            return jsonify({"answer": f"⚠️ ERROR DEL SISTEMA: {error_msg}"})

# --- API 2: PREDICCIÓN ML ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict():
    try:
        data = request.json
        lang = data.get('lang', 'es')
        prompt = f"Analiza exoplaneta: Radio={data.get('koi_prad')}, Temp={data.get('koi_steff')}. Responde JSON: prediccion, probabilidad, analisis_tecnico. Idioma: {lang}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", temperature=0.5,
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
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192",
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
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192", max_tokens=60
        )
        return jsonify({"comment": chat_completion.choices[0].message.content})
    except:
        return jsonify({"comment": "Fin de simulación."})

if __name__ == "__main__":
    app.run(debug=True)
