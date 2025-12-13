import os
import json
import logging
import requests
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# --- CONFIGURACIÓN ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

base_dir = Path(__file__).resolve().parent
env_path = base_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GROQ_API_KEY") 
client = None
MODEL_ID = "llama-3.3-70b-versatile" 

if API_KEY:
    try:
        client = Groq(api_key=API_KEY)
        print(f"✅ NÚCLEO AZTLÁN ONLINE: {MODEL_ID}")
    except Exception as e:
        print(f"⚠️ FALLO EN NÚCLEO IA: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('explorador.html')

# --- API 1: PREDICCIÓN (CON NOMBRE FLEXIBLE) ---
@app.route('/api/aztlan-predict', methods=['POST'])
def predict_endpoint():
    data = request.get_json()
    # Si no llega nombre, ponemos uno por defecto
    planet_name = data.get('planet_name', 'OBJETO_X-99')
    
    koi_prad = data.get('koi_prad', 0)
    koi_srad = data.get('koi_srad', 0)
    koi_period = data.get('koi_period', 0)
    koi_steff = data.get('koi_steff', 0)

    if not client: return jsonify({"error": "NÚCLEO DESCONECTADO"})

    system_prompt = (
        f"Eres AZTLAN, IA de la nave. Reporta al CAPITÁN sobre el objetivo designado: '{planet_name}'.\n"
        "Reglas: Radios < 2.5 Tierra + periodo estable = Confirmado. Radios gigantes + calor extremo = Falso.\n"
        "Salida JSON: { \"prediccion\": \"TEXTO\", \"probabilidad\": \"XX%\", \"analisis_tecnico\": \"Texto breve\", \"habitabilidad\": \"Texto breve\" }"
    )
    user_input = f"Datos {planet_name}: Radio={koi_prad}, Estrella={koi_srad}, Periodo={koi_period}, Temp={koi_steff}"

    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            model=MODEL_ID, temperature=0.3, response_format={"type": "json_object"}
        )
        return jsonify(json.loads(response.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)})

# --- API 2: ANÁLISIS A FONDO ---
@app.route('/api/aztlan-deep', methods=['POST'])
def deep_scan_endpoint():
    data = request.get_json()
    planet_name = data.get('planet_name', 'Planeta Desconocido')
    
    user_input = f"Objetivo: {planet_name}. Datos: Radio={data.get('koi_prad')}, Temp={data.get('koi_steff')}."

    system_prompt = (
        "Eres AZTLAN, Oficial Científico.\n"
        f"Genera un 'REPORTE DE COLONIZACIÓN' para el Capitán sobre el mundo '{planet_name}'.\n"
        "Estructura Markdown:\n"
        "1. Atmósfera.\n"
        "2. Gravedad.\n"
        "3. Riesgos.\n"
        "4. Conclusión.\n"
    )

    try:
        chat = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            model=MODEL_ID, temperature=0.7, max_tokens=1000
        )
        return jsonify({"report": chat.choices[0].message.content})
    except Exception as e:
        return jsonify({"report": "Fallo en reporte."})

# --- API 3: CHAT ---
@app.route('/api/nasa-rag', methods=['POST'])
def rag_endpoint():
    data = request.get_json()
    user_query = data.get('user_query', '').strip()
    system_prompt = "Eres AZTLAN. Responde solo sobre astronomía al Capitán."
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
            model=MODEL_ID, temperature=0.7
        )
        return jsonify({"answer": chat.choices[0].message.content})
    except Exception as e: return jsonify({"answer": str(e)})

# --- API 4: IMÁGENES ---
@app.route('/api/nasa-feed', methods=['GET'])
def nasa_feed():
    query = request.args.get('q', 'galaxy')
    try:
        r = requests.get(f"https://images-api.nasa.gov/search?q={query}&media_type=image").json()
        items = r.get('collection', {}).get('items', [])[:10]
        return jsonify([{"url": i['links'][0]['href'], "title": i['data'][0]['title']} for i in items])
    except: return jsonify([])

if __name__ == '__main__':
    print("🚀 AZTLAN v4.1: SISTEMA DE NOMBRES LISTO...")
    app.run(host='0.0.0.0', port=5000)