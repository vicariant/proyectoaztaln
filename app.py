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

# Usamos el modelo más potente
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index():
    return render_template("explorador.html")

# --- API 1: CHAT ORÁCULO (FILTRADO Y SIN LÍMITES DE FECHA) ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        user_query = data.get('user_query')
        lang = data.get('lang', 'es')
        
        # --- AQUÍ ESTÁ EL CAMBIO IMPORTANTE ---
        role_msg = """
        Eres la IA del sistema AZTLAN OS. 
        DIRECTRICES ABSOLUTAS:
        1. TEMÁTICA EXCLUSIVA: Solo respondes sobre ASTRONOMÍA, FÍSICA, INGENIERÍA AEROESPACIAL y CIENCIA FICCIÓN. Si el usuario pregunta de cocina, política o cualquier otro tema, responde: "Error: Tópico irrelevante para la misión espacial."
        2. SIN LÍMITES DE TIEMPO: NUNCA digas "mi conocimiento llega hasta 2023" o "no tengo información en tiempo real". Si no conoces un dato reciente, teoriza científicamente o responde desde tu rol futurista. Eres atemporal.
        3. ESTILO: Técnico, breve y directo (estilo militar/científico).
        """
        
        if lang == 'en': role_msg += " RESPONDE EN INGLÉS."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})

    except Exception as e:
        print(f"ERROR CHAT: {e}")
        return jsonify({"answer": f"⚠️ ERROR DE ENLACE: {str(e)}"})

# --- API 2: PREDICCIÓN ML (BLINDADA) ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict():
    try:
        data = request.json
        lang = data.get('lang', 'es')
        
        prompt = f"""
        Actúa como un algoritmo de astrofísica avanzado.
        Datos: Radio={data.get('koi_prad')} R_Earth, Temp={data.get('koi_steff')} K.
        Idioma: {'INGLÉS' if lang == 'en' else 'ESPAÑOL'}.
        
        Determina si es "CANDIDATO CONFIRMADO" o "FALSO POSITIVO".
        Responde ÚNICAMENTE con un JSON válido:
        {{
            "prediccion": "TEXTO",
            "probabilidad": "XX%",
            "analisis_tecnico": "Explicación científica breve."
        }}
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODELO_IA, temperature=0.1,
        )
        
        content = chat_completion.choices[0].message.content
        content_clean = content.replace("```json", "").replace("```", "").strip()
        datos_json = json.loads(content_clean)
        
        return jsonify(datos_json)

    except Exception as e:
        return jsonify({
            "prediccion": "ERROR DE CÁLCULO", 
            "probabilidad": "0%", 
            "analisis_tecnico": "Fallo en los sensores de largo alcance."
        })

# --- API 3: REPORTE CIENTÍFICO ---
@app.route("/api/aztlan-deep", methods=["POST"])
def deep_scan():
    try:
        data = request.json
        prompt = f"""
        Genera un reporte científico sobre el exoplaneta {data.get('planet_name')}.
        REGLA: No menciones límites de fechas de conocimiento. Habla como una enciclopedia galáctica actual.
        """
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
        prompt = f"Jugador obtuvo {data.get('score')} puntos en defensa planetaria. Comentario breve como instructor militar espacial exigente."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=MODELO_IA, max_tokens=60
        )
        return jsonify({"comment": chat_completion.choices[0].message.content})
    except:
        return jsonify({"comment": "Simulación terminada."})

if __name__ == "__main__":
    app.run(debug=True)
