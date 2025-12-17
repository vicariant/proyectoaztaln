from flask import Flask, render_template, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

TOA_API_KEY = os.getenv('TOA_API_KEY', '')
TOA_BASE_URL = 'https://theorangealliance.org/api'
TOA_HEADERS = {'X-TOA-Key': TOA_API_KEY, 'Content-Type': 'application/json'}

MOCK_DATA = {
    'events': [
        {'event_key': '2425-MX-CDMX-01', 'event_name': 'Torneo Regional CDMX', 'start_date': '2025-01-15', 'city': 'Ciudad de México', 'venue': 'Centro de Convenciones'},
        {'event_key': '2425-MX-MTY-01', 'event_name': 'Torneo Regional Monterrey', 'start_date': '2025-02-10', 'city': 'Monterrey', 'venue': 'Arena Tecnológica'},
        {'event_key': '2425-MX-GDL-01', 'event_name': 'Torneo Regional Guadalajara', 'start_date': '2025-02-20', 'city': 'Guadalajara', 'venue': 'Expo Guadalajara'}
    ],
    'teams': [
        {'team_key': '28254', 'team_number': 28254, 'team_name_short': 'Tech Saurus', 'city': 'Ciudad de México', 'rookie_year': 2023, 'rp_total': 145},
        {'team_key': '28255', 'team_number': 28255, 'team_name_short': 'Decode Masters', 'city': 'Monterrey', 'rookie_year': 2022, 'rp_total': 167},
        {'team_key': '11111', 'team_number': 11111, 'team_name_short': 'Robo Warriors', 'city': 'Guadalajara', 'rookie_year': 2021, 'rp_total': 132},
        {'team_key': '22222', 'team_number': 22222, 'team_name_short': 'Cyber Knights', 'city': 'Puebla', 'rookie_year': 2024, 'rp_total': 98},
        {'team_key': '33333', 'team_number': 33333, 'team_name_short': 'Code Breakers', 'city': 'Querétaro', 'rookie_year': 2023, 'rp_total': 115}
    ],
    'team_details': {
        '28254': {'awards': [{'award_name': 'Inspire Award'}, {'award_name': 'Winning Alliance Captain'}], 'rankings': {'rp': 145, 'rank': 3}},
        '28255': {'awards': [{'award_name': 'Think Award'}, {'award_name': 'Connect Award'}], 'rankings': {'rp': 167, 'rank': 1}},
        '11111': {'awards': [{'award_name': 'Design Award'}], 'rankings': {'rp': 132, 'rank': 5}},
        '22222': {'awards': [], 'rankings': {'rp': 98, 'rank': 12}},
        '33333': {'awards': [{'award_name': 'Innovate Award'}], 'rankings': {'rp': 115, 'rank': 8}}
    }
}

CHATBOT_RESPONSES = {
    'puntos': 'En FTC DECODE, los puntos se otorgan por: colocar muestras en zonas (5-10 pts), ascender niveles (15-30 pts), y parkear en zonas seguras (5-15 pts). Los Ranking Points (RP) se calculan sumando puntos de clasificación + bonificaciones por premios.',
    'premios': 'Premios principales: Inspire Award (+15 RP), Think Award (+10 RP), Connect Award (+10 RP), Innovate Award (+8 RP), Design Award (+8 RP), Control Award (+5 RP), Motivate Award (+5 RP), Winning Alliance (+10 RP).',
    'clasificar': 'Para clasificar se necesitan típicamente más de 120 RP totales. Los equipos en la "Lista Verde" (clasificados retroactivos) avanzan automáticamente.',
    'robot': 'El robot debe caber en 18"x18"x18" al inicio, puede expandirse durante el match. Peso máximo: 42 lbs (19 kg). Debe usar componentes legales FIRST.',
    'autonomo': 'Período autónomo: 30 segundos sin control humano. Bonificaciones por parkear, colocar muestras y completar navegación.',
    'teleop': 'TeleOperado: 2 minutos con control manual. Se manipulan elementos, ascender estructuras y posicionar para EndGame.',
    'endgame': 'Últimos 30 segundos del TeleOp. Puntos extra por ascender niveles, parkear en zonas específicas y completar tareas de cierre.',
    'falta': 'Faltas: contacto destructivo (Minor/Major), salir del campo, interferir con oponente, violar seguridad. Major Fouls dan puntos al oponente.'
}

def fetch_api(endpoint, params=None):
    if not TOA_API_KEY:
        return None
    try:
        r = requests.get(f'{TOA_BASE_URL}/{endpoint}', headers=TOA_HEADERS, params=params, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

@app.route('/')
def index():
    return render_template('ftc.html')

@app.route('/api/ftc-mexico-data')
def get_ftc_mexico_data():
    events = fetch_api('events', {'region_key': 'MX', 'season_key': '2425'}) or MOCK_DATA['events']
    teams = fetch_api('teams', {'region_key': 'MX'}) or MOCK_DATA['teams']
    return jsonify({'status': 'success', 'source': 'live' if TOA_API_KEY else 'mock', 'events': events, 'teams': teams})

@app.route('/api/team-detail/<team_key>')
def get_team_detail(team_key):
    awards = fetch_api(f'team/{team_key}/awards')
    rankings = fetch_api(f'team/{team_key}/rankings/2425')
    
    if awards and rankings:
        return jsonify({'status': 'success', 'source': 'live', 'awards': awards, 'rankings': rankings})
    
    details = MOCK_DATA['team_details'].get(team_key, {'awards': [], 'rankings': {'rp': 0, 'rank': 0}})
    return jsonify({'status': 'success', 'source': 'mock', **details})

@app.route('/api/nasa-rag', methods=['POST'])
def nasa_rag_chatbot():
    question = request.json.get('question', '').lower()
    response = 'Como Juez Neutral de FTC, consulta el Game Manual oficial para detalles específicos. Pregunta sobre: puntos, premios, clasificación, robot, autónomo, teleop, endgame o faltas.'
    
    for keyword, answer in CHATBOT_RESPONSES.items():
        if keyword in question:
            response = f'⚖️ **Respuesta del Juez Neutral**: {answer}'
            break
    
    return jsonify({'status': 'success', 'response': response, 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
