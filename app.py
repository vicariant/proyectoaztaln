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

# Llave opcional para The Orange Alliance (FTC Data)
TOA_KEY = os.environ.get("TOA_API_KEY", "") 
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index():
    return render_template("explorador.html")

@app.route("/ftc")
def ftc_dashboard():
    return render_template("ftc.html")

# --- API MAESTRA: CHAT CON PERSONALIDAD VARIABLE ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        user_query = data.get('user_query')
        lang = data.get('lang', 'es')
        mode = data.get('mode', 'nasa') # <--- AQUÍ ESTÁ EL TRUCO (Por defecto es NASA)
        
        # 1. PERSONALIDAD FTC (ROBÓTICA)
        if mode == 'ftc':
            role_msg = """
            Eres la IA OFICIAL de la temporada FIRST Tech Challenge 2025-2026: DECODE.
            TUS REGLAS:
            1. Eres un experto en el Game Manual Part 1 y Part 2 de DECODE.
            2. Hablas con términos técnicos de robótica (Chasis, Odometría, Servos, Control Hub, Java, Blocks).
            3. Tu tono es útil, estratégico y motivador para equipos como Waachma y Techkalli.
            4. Si te preguntan de astronomía, responde: "Módulo astronómico desactivado. Centrándose en el robot."
            """
        
        # 2. PERSONALIDAD AZTLÁN (ESPACIO)
        else:
            role_msg = """
            Eres la IA del sistema AZTLAN OS. 
            TUS REGLAS:
            1. Solo respondes sobre ASTRONOMÍA, FÍSICA y CIENCIA FICCIÓN.
            2. Actúa como una interfaz de nave espacial futurista.
            3. Si te preguntan de robótica o cocina, di: "Error: Tópico irrelevante para la misión interestelar."
            """
        
        if lang == 'en': role_msg += " RESPONDE EN INGLÉS."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"answer": f"⚠️ ERROR DE SISTEMA: {str(e)}"})

# --- API DATOS FTC (TOA / MOCK) ---
@app.route("/api/ftc-real", methods=["GET"])
def ftc_data():
    if TOA_KEY:
        try:
            headers = {"Content-Type": "application/json", "X-TOA-Key": TOA_KEY}
            events = requests.get("https://theorangealliance.org/api/event?region_key=MX&season_key=2425", headers=headers).json()
            return jsonify({"source": "TOA_LIVE", "data": events[:5]})
        except: pass

    # Datos simulados de respaldo si no hay API Key real
    mock_data = [{
        "event_name": "Regional CDMX DECODE",
        "date": "2025-12-13",
        "location": "PrepaTec CDMX",
        "matches": [
            {"match": "Q-1", "red": "28254 Waachma", "red_score": 85, "blue": "28255 Techkalli", "blue_score": 92},
            {"match": "Q-2", "red": "11111 Voltec", "red_score": 110, "blue": "99999 Cyber", "blue_score": 45}
        ],
        "rankings": [{"rank": 1, "team": "28254 Waachma", "rp": 2.5}, {"rank": 2, "team": "28255 Techkalli", "rp": 2.0}]
    }]
    return jsonify({"source": "DECODE_NET", "data": mock_data})

# --- OTRAS APIS (JUEGOS/NASA) ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict(): return jsonify({"prediccion":"OFFLINE","probabilidad":"0%","analisis_tecnico":"..."})
@app.route("/api/game-analysis", methods=["POST"])
def game_analysis(): return jsonify({"comment":"Buen juego."})
@app.route("/api/nasa-feed")
def nasa_feed(): return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
