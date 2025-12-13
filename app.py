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
    # Asegúrate de que tu archivo HTML se llame 'explorador.html' en la carpeta templates
    return render_template("explorador.html")

# --- API 1: CHAT ORÁCULO (Multilingüe) ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    data = request.json
    user_query = data.get('user_query')
    lang = data.get('lang', 'es')
    
    role_msg = "Eres la IA del sistema AZTLAN OS. Responde de forma breve, técnica y futurista."
    if lang == 'en':
        role_msg += " RESPONDE EN INGLÉS."
    else:
        role_msg += " RESPONDE EN ESPAÑOL."

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model="llama3-8b-8192", temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
   except Exception as e:
        # Esto imprimirá el error real en tu pantalla de chat
        error_message = str(e)
        print(f"ERROR CRÍTICO: {error_message}")
        
        if "401" in error_message:
            return jsonify({"answer": "ERROR 401: La llave API está mal puesta en Heroku. Revisa que no tenga espacios."})
        elif "404" in error_message:
            return jsonify({"answer": "ERROR 404: El modelo de IA no existe. Avisa al desarrollador."})
        else:
            return jsonify({"answer": f"ERROR DESCONOCIDO: {error_message}"})
# --- API 2: PREDICCIÓN ML (Simulada con IA) ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict():
    data = request.json
    lang = data.get('lang', 'es')
    
    # Usamos la IA para simular un análisis de Machine Learning complejo
    prompt = f"""
    Actúa como un algoritmo de clasificación de exoplanetas (Random Forest).
    Analiza: Radio={data.get('koi_prad')} R_Earth, Temp={data.get('koi_steff')} K.
    Idioma de respuesta: {'INGLÉS' if lang == 'en' else 'ESPAÑOL'}.
    
    1. Determina si es CANDIDATO CONFIRMADO o FALSO POSITIVO (basado en si el radio es < 2.5 y temperatura < 350K).
    2. Da una probabilidad (ej. 98.4%).
    3. Da una razón técnica muy breve (1 frase).
    
    Formato JSON esperado: {{ "prediccion": "...", "probabilidad": "...", "analisis_tecnico": "..." }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Responde solo en JSON válido."}, {"role": "user", "content": prompt}],
            model="llama3-8b-8192", temperature=0.5,
        )
        return chat_completion.choices[0].message.content
    except:
        # Fallback si falla la IA
        return jsonify({
            "prediccion": "ERROR", 
            "probabilidad": "0%", 
            "analisis_tecnico": "Fallo en sensores / Sensor failure."
        })

# --- API 3: REPORTE CIENTÍFICO ---
@app.route("/api/aztlan-deep", methods=["POST"])
def deep_scan():
    data = request.json
    lang = data.get('lang', 'es')
    prompt = f"Genera un reporte científico breve sobre el exoplaneta {data.get('planet_name')}."
    if lang == 'en': prompt += " Write in English."
    
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
        url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"
        r = requests.get(url).json()
        items = r['collection']['items'][:8]
        images = [{"url": item['links'][0]['href'], "title": item['data'][0]['title']} for item in items if 'links' in item]
        return jsonify(images)
    except:
        return jsonify([])

# --- API 5: ANÁLISIS DE JUEGO (GAME OVER AI) ---
@app.route("/api/game-analysis", methods=["POST"])
def game_analysis():
    data = request.json
    score = data.get('score', 0)
    lang = data.get('lang', 'es')
    prompt = f"El usuario obtuvo {score} puntos en el simulador de defensa espacial. Eres un comandante estricto. Dale un comentario de 1 frase juzgando su desempeño."
    if lang == 'en': prompt += " Write in English."
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192", max_tokens=60
        )
        return jsonify({"comment": chat_completion.choices[0].message.content})
    except:
        return jsonify({"comment": "Simulación terminada."})

if __name__ == "__main__":
    app.run(debug=True)


