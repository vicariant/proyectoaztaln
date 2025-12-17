import os
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# ==========================================
# 🔑 CONFIGURACIÓN DE LLAVES (API KEYS)
# ==========================================

# 1. LLAVES DE LA API OFICIAL DE FIRST (FTC EVENTS)
# Estas son las que recibiste en el correo.
FTC_USERNAME = os.environ.get("FTC_USERNAME", "tennyson")
FTC_TOKEN = os.environ.get("FTC_TOKEN", "5EB69BCF-B53C-4B69-8874-CBF204FAD462")
BASE_URL = "https://ftc-events.firstinspires.org/v2.0/2025" # Temporada 2025-2026

# 2. LLAVE DE INTELIGENCIA ARTIFICIAL (GROQ)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route("/")
def index():
    return render_template("ftc.html")

# ==========================================
# API 1: CHATBOT JUEZ (IA)
# ==========================================
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        user_query = data.get('user_query')
        
        if not client: 
            return jsonify({"answer": "IA Desconectada. Configura GROQ_API_KEY."})
            
        role_msg = """Eres la IA Juez Oficial de FTC (First Tech Challenge).
        Responde dudas del reglamento 'DECODE' de forma breve, técnica y neutral."""
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model="llama-3.3-70b-versatile", temperature=0.5
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
    except: return jsonify({"answer": "Error de conexión neuronal."})

# ==========================================
# API 2: CONEXIÓN OFICIAL FIRST (DATOS REALES)
# ==========================================
@app.route("/api/ftc-mexico-data", methods=["GET"])
def ftc_data():
    data = {"events": [], "teams": [], "source": "BACKUP"}
    
    # AUTENTICACIÓN OFICIAL (Basic Auth)
    auth = (FTC_USERNAME, FTC_TOKEN)
    
    try:
        # 1. OBTENER EQUIPOS DE MÉXICO (Endpoint Oficial)
        # Pedimos todos los equipos registrados en el país "MX"
        res_teams = requests.get(f"{BASE_URL}/teams?country=MX", auth=auth)
        
        if res_teams.status_code == 200:
            teams_list = res_teams.json().get('teams', [])
            for t in teams_list:
                data["teams"].append({
                    "id": t['teamNumber'],
                    "n": t['nameShort'],
                    "l": f"{t['city']}, {t['stateProv']}",
                    "r": t['rookieYear'],
                    "rp": 0 # El RP se calcula en el detalle
                })
            data["source"] = "OFFICIAL_API_V2"

        # 2. OBTENER EVENTOS DE MÉXICO
        res_events = requests.get(f"{BASE_URL}/events?country=MX", auth=auth)
        if res_events.status_code == 200:
            events_list = res_events.json().get('events', [])
            for ev in events_list:
                data["events"].append({
                    "n": ev['name'],
                    "d": ev['dateStart'].split('T')[0],
                    "c": f"{ev['city']}, {ev['stateProv']}",
                    "k": "CMP" if "Championship" in ev['name'] else "QT"
                })

    except Exception as e:
        print(f"Error conectando a FIRST: {e}")

    # --- DATOS DE RESPALDO (Por si falla la conexión o es muy temprano en la temporada) ---
    if not data["teams"]:
        data["teams"] = [
            {"id": 28254, "n": "WAACHMA", "l": "Tecámac, MEX", "r": 2024, "rp": 0},
            {"id": 28255, "n": "TECHKALLI", "l": "Tecámac, MEX", "r": 2024, "rp": 0},
            {"id": 11111, "n": "VOLTEC", "l": "Monterrey, NL", "r": 2016, "rp": 0}
        ]
        data["source"] = "SIMULATION_MODE"

    if not data["events"]:
        data["events"] = [
            {"n": "Regional CDMX (Simulado)", "d": "2025-12-01", "c": "CDMX", "k": "QT"},
            {"n": "Mexico Championship (Simulado)", "d": "2026-02-02", "c": "CDMX", "k": "CMP"}
        ]

    return jsonify(data)

# ==========================================
# API 3: DETALLE DE EQUIPO (SIMULACIÓN INTELIGENTE)
# ==========================================
@app.route("/api/team-detail/<id>")
def team_detail(id):
    # La API oficial limita mucho las llamadas por minuto. 
    # Para que tu página no se bloquee, simularemos los puntos (RP) y premios
    # basándonos en si el equipo está en tu "Lista Verde" o al azar.
    
    import random
    
    # Lista de equipos "TOP" que suelen ganar premios
    top_teams = ["28254", "28255", "11111", "16380"]
    
    awards = []
    rp = random.randint(50, 200) # RP Base
    
    # Si es uno de tus equipos, le damos mejores stats simulados
    if str(id) in top_teams:
        rp = random.randint(250, 400)
        awards = [{"award_name": "Inspire Award Winner"}, {"award_name": "Winning Alliance Captain"}]
    
    return jsonify({
        "rankings": {"rp": rp, "rank": random.randint(1, 20)},
        "awards": awards
    })

if __name__ == "__main__":
    app.run(debug=True)
