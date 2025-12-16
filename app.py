import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# --- CONFIGURACIÓN ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Si no tienes llave TOA, el sistema usará datos simulados automáticamente
TOA_API_KEY = os.environ.get("TOA_API_KEY", "") 

client = Groq(api_key=GROQ_API_KEY)
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index(): return render_template("explorador.html")

@app.route("/ftc")
def ftc_dashboard(): return render_template("ftc.html")

# --- API 1: CHATBOT JUEZ (NEUTRAL) ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        mode = data.get('mode', 'nasa')
        user_query = data.get('user_query')
        
        if mode == 'ftc':
            role_msg = """
            Eres la IA Juez Oficial de FTC DECODE (2025-2026).
            MANDATOS:
            1. Neutralidad absoluta. Ayudas a todos los equipos por igual.
            2. Respuestas basadas estrictamente en el Game Manual Part 1 y 2.
            3. Sé breve, técnico y profesional.
            """
        else:
            role_msg = "Eres la IA de AZTLAN OS. Solo hablas de misiones espaciales."
            
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.6,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
    except: return jsonify({"answer": "Error de enlace con el Juez Virtual."})

# --- API 2: DATOS GENERALES (EVENTOS Y EQUIPOS MX) ---
@app.route("/api/ftc-mexico-data", methods=["GET"])
def ftc_toa_data():
    data = {"events": [], "teams": [], "source": "BACKUP"}
    
    if TOA_API_KEY:
        headers = {'Content-Type': 'application/json', 'X-TOA-Key': TOA_API_KEY, 'X-Application-Origin': 'AztlanOS'}
        try:
            # 1. EVENTOS MX
            res_ev = requests.get('https://theorangealliance.org/api/event?region_key=MX&season_key=2425', headers=headers)
            if res_ev.status_code == 200:
                for ev in res_ev.json():
                    data["events"].append({
                        "key": ev['event_key'],
                        "name": ev['event_name'],
                        "date": ev['start_date'],
                        "status": "🟢 CONFIRMADO" if ev['is_public'] else "📅 PENDIENTE",
                        "url": f"https://theorangealliance.org/events/{ev['event_key']}"
                    })
                data["source"] = "TOA_LIVE"

            # 2. EQUIPOS MX (Activos)
            res_tm = requests.get('https://theorangealliance.org/api/team?region_key=MX&last_active=2425', headers=headers)
            if res_tm.status_code == 200:
                teams = res_tm.json()
                teams.sort(key=lambda x: x['team_number'])
                for t in teams:
                    data["teams"].append({
                        "id": t['team_number'],
                        "name": t['team_name_short'],
                        "loc": f"{t['city']}, {t['state_prov']}"
                    })
        except: pass

    # DATOS DE RESPALDO (Si falla la API o no hay key)
    if not data["events"]:
        data["events"] = [
            {"name": "Regional CDMX", "date": "2025-12-13", "status": "🟢 EN CURSO", "url": "#"},
            {"name": "Regional Monterrey", "date": "2026-01-10", "status": "📅 FUTURO", "url": "#"}
        ]
    if not data["teams"]:
        data["teams"] = [
            {"id": 28254, "name": "Waachma", "loc": "Tecámac"},
            {"id": 28255, "name": "Techkalli", "loc": "Tecámac"},
            {"id": 11111, "name": "Voltec", "loc": "Monterrey"},
            {"id": 12345, "name": "CyberRhinos", "loc": "Querétaro"}
        ]
    
    return jsonify(data)

# --- API 3: DETALLE DE EQUIPO (PARA SCOUTING Y CÁLCULOS) ---
@app.route("/api/team-detail/<team_id>", methods=["GET"])
def team_detail(team_id):
    # Esta ruta busca premios y rankings para hacer tus cálculos
    mock_awards = []
    rp = 0
    
    if TOA_API_KEY:
        headers = {'Content-Type': 'application/json', 'X-TOA-Key': TOA_API_KEY, 'X-Application-Origin': 'AztlanOS'}
        try:
            # Rankings
            res_rank = requests.get(f'https://theorangealliance.org/api/team/{team_id}/results/2425', headers=headers)
            if res_rank.status_code == 200:
                # Sumamos RP de todos los eventos
                for r in res_rank.json():
                    rp += r.get('ranking_points', 0)
            
            # Premios
            res_aw = requests.get(f'https://theorangealliance.org/api/team/{team_id}/awards/2425', headers=headers)
            if res_aw.status_code == 200:
                mock_awards = res_aw.json()
        except: pass
    
    # Simulación para pruebas si no hay datos reales aun
    if not mock_awards and team_id == "28254":
        mock_awards = [{"award_name": "Inspire Award Winner", "recipients": [{"team_key": "28254"}]}]
        rp = 350
        
    return jsonify({"rp": rp, "awards": mock_awards})

if __name__ == "__main__":
    app.run(debug=True)
