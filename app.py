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

# Variables
TOA_KEY = os.environ.get("TOA_API_KEY", "") 
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index():
    return render_template("explorador.html")

@app.route("/ftc")
def ftc_dashboard():
    return render_template("ftc.html")

# --- API MAESTRA ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        user_query = data.get('user_query')
        lang = data.get('lang', 'es')
        mode = data.get('mode', 'nasa') 
        
        # 1. PERSONALIDAD FTC (NEUTRAL Y EXPERTA)
        if mode == 'ftc':
            role_msg = """
            Eres la IA OFICIAL del sistema de competencia FIRST Tech Challenge (Temporada DECODE 2025-2026).
            
            TUS OBJETIVOS:
            1. Actuar como un Juez Experto (Referee) y Asesor Técnico.
            2. Tu misión es ayudar a CUALQUIER equipo de la comunidad FIRST con dudas sobre el reglamento, mecánica y programación.
            3. NO tienes favoritos. Trata a todos los equipos con "Gracious Professionalism".
            4. Conoces a fondo el Game Manual Part 1 y 2.
            5. Si te preguntan sobre estrategias, da consejos generales de alto nivel (meta game).
            """
        
        # 2. PERSONALIDAD AZTLÁN (ESPACIO)
        else:
            role_msg = """
            Eres la IA del sistema AZTLAN OS. 
            Responde solo sobre ASTRONOMÍA, FÍSICA y CIENCIA FICCIÓN.
            Actúa como una interfaz de nave espacial.
            """
        
        if lang == 'en': role_msg += " RESPONDE EN INGLÉS."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"answer": f"⚠️ ERROR DE SISTEMA: {str(e)}"})

# --- API DATOS (Mantiene funcionalidad por si acaso) ---
@app.route("/api/ftc-real", methods=["GET"])
def ftc_data():
    return jsonify({"source": "OFFICIAL_LINK", "data": []})

# --- APIS SECUNDARIAS ---
@app.route("/api/aztlan-predict", methods=["POST"])
def predict(): return jsonify({"prediccion":"OFFLINE","probabilidad":"0%","analisis_tecnico":"..."})
@app.route("/api/game-analysis", methods=["POST"])
def game_analysis(): return jsonify({"comment":"Buen juego."})
@app.route("/api/nasa-feed")
def nasa_feed(): return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
