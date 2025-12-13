import os
import requests
import random
import json
import re # Herramienta para limpieza de texto
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Configuración de Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Usamos el modelo nuevo y potente
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
        
        role_msg = "Eres la IA del sistema AZTLAN OS. Responde de forma técnica y breve."
        if lang == 'en': role_msg += " RESPONDE EN INGLÉS."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})

    except Exception as e:
        print(f"ERROR CHAT: {e}")
        return jsonify({"answer": f"⚠️ ERROR DE SISTEMA: {str(e)}"})

# --- API 2: PREDICCIÓN ML (BLINDADA) ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict():
    try:
        data = request.json
        lang = data.get('lang', 'es')
        
        # Prompt estricto para JSON
        prompt = f"""
        Actúa como un algoritmo científico.
        Datos: Radio={data.get('koi_prad')} R_Earth, Temp={data.get('koi_steff')} K.
        Idioma: {'INGLÉS' if lang == 'en' else 'ESPAÑOL'}.
        
        Tarea: Determina si es "CANDIDATO CONFIRMADO" o "FALSO POSITIVO".
        Responde ÚNICAMENTE con un JSON válido con este formato:
        {{
            "prediccion": "TEXTO_AQUI",
            "probabilidad": "XX%",
            "analisis_tecnico": "Explicación breve."
        }}
        NO añadidas comillas markdown (```json). Solo el JSON puro.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODELO_IA, temperature=0.1, # Temperatura baja para ser preciso
        )
        
        content = chat_completion.choices[0].message.content
        
        # --- LIMPIEZA DE RESPUESTA (EL TRUCO) ---
        # A veces la IA pone ```json ... ```, esto lo quita:
        content_clean = content.replace("```json", "").replace("```", "").strip()
        
        # Intentamos convertirlo a diccionario Python y luego a JSON real
        datos_json = json.loads(content_clean)
        
        return jsonify(datos_json)

    except Exception as e:
        print(f"ERROR PREDICT: {e}")
        # Si falla, devolvemos un JSON de error manual para que no se rompa la web
        return jsonify({
            "prediccion": "ERROR DE CÁLCULO", 
            "probabilidad": "0%", 
            "analisis_tecnico": f"No se pudo procesar la respuesta neuronal. Detalles: {str(e)}"
        })

# --- API 3: REPORTE CIENTÍFICO ---
@app.route("/api/aztlan-deep", methods=["POST"])
def deep_scan():
    try:
        data = request.json
        prompt = f"Genera un reporte científico muy breve sobre el exoplaneta {data.get('planet_name')}."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=MODELO_IA,
        )
        return jsonify({"report": chat_completion.choices[0].message.content})
    except:
        return jsonify({"report": "Datos insuficientes para el reporte."})

# --- API 4: GALERÍA NASA ---
@app.route("/api/nasa-feed")
def nasa_feed():
    try:
        query = request.args.get('q', 'galaxy')
        url = f"[https://images-api.nasa.gov/search?q=](https://images-api.nasa.gov/search?q=){query}&media_type=image"
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
        prompt = f"Jugador obtuvo {data.get('score')} puntos. Comentario breve militar exigente."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=MODELO_IA, max_tokens=60
        )
        return jsonify({"comment": chat_completion.choices[0].message.content})
    except:
        return jsonify({"comment": "Simulación terminada."})

if __name__ == "__main__":
    app.run(debug=True)
