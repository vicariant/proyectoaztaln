import os
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN DE LLAVES (KEYS)
# ==========================================
# Pon tus llaves aquí o en las "Config Vars" de Heroku
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TOA_API_KEY = os.environ.get("TOA_API_KEY", "") 

# Configuración de IA
client = Groq(api_key=GROQ_API_KEY)
MODELO_IA = "llama-3.3-70b-versatile"

# Temporada Actual (Cambiar a '2526' cuando inicie oficialmente DECODE)
SEASON_KEY = "2425" 

@app.route("/")
def index():
    return render_template("explorador.html")

@app.route("/ftc")
def ftc_dashboard():
    return render_template("ftc.html")

# ==========================================
# API 1: CHATBOT JUEZ NEUTRAL
# ==========================================
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        mode = data.get('mode', 'nasa')
        user_query = data.get('user_query')
        
        if mode == 'ftc':
            role_msg = """
            Eres la IA Juez Oficial de FIRST Tech Challenge.
            TU ROL:
            1. Actuar como 'Head Referee'. Eres neutral, técnico y preciso.
            2. Tu base de conocimiento es el Game Manual Part 1 y 2.
            3. Ayudas a cualquier equipo (Waachma, Techkalli, Voltec, etc.) por igual.
            4. Responde dudas sobre: Autonomous, TeleOp, End Game, Penalizaciones y Puntuación.
            """
        else:
            role_msg = "Eres la IA del sistema AZTLAN OS. Respondes como una computadora de nave espacial."
            
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": role_msg}, 
                {"role": "user", "content": user_query}
            ],
            model=MODELO_IA, temperature=0.6,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"answer": f"Error de comunicación con el Juez: {str(e)}"})

# ==========================================
# API 2: DATOS GENERALES (EVENTOS Y EQUIPOS)
# ==========================================
@app.route("/api/ftc-mexico-data", methods=["GET"])
def ftc_mexico_data():
    data = {"events": [], "teams": [], "source": "BACKUP"}
    
    # Intentar conexión real con TOA
    if TOA_API_KEY:
        headers = {
            'Content-Type': 'application/json',
            'X-TOA-Key': TOA_API_KEY,
            'X-Application-Origin': 'AztlanDecode'
        }
        try:
            # 1. OBTENER EVENTOS DE MÉXICO
            res_ev = requests.get(f'https://theorangealliance.org/api/event?region_key=MX&season_key={SEASON_KEY}', headers=headers)
            if res_ev.status_code == 200:
                for ev in res_ev.json():
                    data["events"].append({
                        "event_name": ev['event_name'],
                        "start_date": ev['start_date'].split('T')[0],
                        "city": ev['city'],
                        "state": ev['state_prov'],
                        "venue": ev['venue'],
                        "type": ev['event_type_key'] # CMP, QT, etc.
                    })
                data["source"] = "TOA_LIVE"

            # 2. OBTENER EQUIPOS DE MÉXICO (Activos)
            res_tm = requests.get(f'https://theorangealliance.org/api/team?region_key=MX&last_active={SEASON_KEY}', headers=headers)
            if res_tm.status_code == 200:
                teams_raw = res_tm.json()
                # Ordenar por número de equipo
                teams_raw.sort(key=lambda x: x['team_number'])
                
                for t in teams_raw:
                    # Intentar buscar RP totales si están disponibles en el objeto (a veces TOA no lo manda directo aquí)
                    data["teams"].append({
                        "team_key": t['team_key'],
                        "team_number": t['team_number'],
                        "team_name_short": t['team_name_short'],
                        "city": t['city'],
                        "state": t['state_prov'],
                        "rookie_year": t['rookie_year'],
                        "rp_total": 0 # Se llenará en el detalle o con otra llamada si fuera necesario
                    })

        except Exception as e:
            print(f"Error TOA: {e}")

    # --- DATOS DE RESPALDO (SI FALLA TOA) ---
    if not data["events"]:
        data["events"] = [
            {"event_name": "Regional CDMX", "start_date": "2025-12-13", "city": "Mexico City", "state": "CMX", "venue": "PrepaTec CCM", "type": "QT"},
            {"event_name": "Regional Monterrey", "start_date": "2026-01-10", "city": "Monterrey", "state": "NLE", "venue": "PrepaTec Garza Sada", "type": "QT"},
            {"event_name": "Campeonato Nacional", "start_date": "2026-03-15", "city": "TBD", "state": "MX", "venue": "TBD", "type": "CMP"}
        ]
    
    if not data["teams"]:
        # Lista simulada para que no se vea vacío
        data["teams"] = [
            {"team_key": "28254", "team_number": 28254, "team_name_short": "Waachma", "city": "Tecámac", "state": "MEX", "rookie_year": 2024, "rp_total": 350},
            {"team_key": "28255", "team_number": 28255, "team_name_short": "Techkalli", "city": "Tecámac", "state": "MEX", "rookie_year": 2024, "rp_total": 320},
            {"team_key": "11111", "team_number": 11111, "team_name_short": "Voltec", "city": "Monterrey", "state": "NLE", "rookie_year": 2016, "rp_total": 410}
        ]

    return jsonify(data)

# ==========================================
# API 3: DETALLE DE EQUIPO (PREMIOS Y RANKINGS)
# ==========================================
@app.route("/api/team-detail/<team_key>", methods=["GET"])
def team_detail(team_key):
    detail = {"rankings": {"rp": 0, "rank": 0}, "awards": []}
    
    if TOA_API_KEY:
        headers = {'Content-Type': 'application/json', 'X-TOA-Key': TOA_API_KEY, 'X-Application-Origin': 'AztlanDecode'}
        try:
            # 1. OBTENER RANKINGS/RESULTADOS
            res_res = requests.get(f'https://theorangealliance.org/api/team/{team_key}/results/{SEASON_KEY}', headers=headers)
            if res_res.status_code == 200:
                results = res_res.json()
                total_rp = 0
                for r in results:
                    # Sumamos los Ranking Points de todos los eventos jugados
                    total_rp += r.get('ranking_points', 0)
                
                # Asignamos el total
                detail["rankings"]["rp"] = total_rp
                # El rank global es complejo de calcular, lo dejamos en 0 o tomamos el del último evento si existe

            # 2. OBTENER PREMIOS (AWARDS)
            res_aw = requests.get(f'https://theorangealliance.org/api/team/{team_key}/awards/{SEASON_KEY}', headers=headers)
            if res_aw.status_code == 200:
                awards_data = res_aw.json()
                for aw in awards_data:
                    detail["awards"].append({
                        "award_key": aw['award_key'],
                        "award_name": aw['award_name'] # Ej: "Inspire Award Winner"
                    })

        except Exception as e:
            print(f"Error Detalle TOA: {e}")

    # --- SIMULACIÓN PARA WAACHMA (28254) SI NO HAY DATOS ---
    if not detail["awards"] and team_key == "28254":
        detail["rankings"]["rp"] = 150
        detail["awards"] = [
            {"award_name": "Connect Award Winner"},
            {"award_name": "Finalist Alliance Captain"}
        ]
        
    return jsonify(detail)

if __name__ == "__main__":
    app.run(debug=True)
