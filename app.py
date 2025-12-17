from flask import Flask, render_template, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuración de The Orange Alliance API
TOA_API_KEY = os.getenv('TOA_API_KEY', '')
TOA_BASE_URL = 'https://theorangealliance.org/api'
TOA_HEADERS = {
    'X-TOA-Key': TOA_API_KEY,
    'Content-Type': 'application/json'
}

# Datos mock en caso de que no haya API Key
MOCK_EVENTS = [
    {
        'event_key': '2425-MX-CDMX-01',
        'event_name': 'Torneo Regional CDMX',
        'start_date': '2025-01-15',
        'city': 'Ciudad de México',
        'venue': 'Centro de Convenciones'
    },
    {
        'event_key': '2425-MX-MTY-01',
        'event_name': 'Torneo Regional Monterrey',
        'start_date': '2025-02-10',
        'city': 'Monterrey',
        'venue': 'Arena Tecnológica'
    }
]

MOCK_TEAMS = [
    {
        'team_key': '28254',
        'team_number': 28254,
        'team_name_short': 'Tech Saurus',
        'city': 'Ciudad de México',
        'rookie_year': 2023,
        'rp_total': 145
    },
    {
        'team_key': '28255',
        'team_number': 28255,
        'team_name_short': 'Decode Masters',
        'city': 'Monterrey',
        'rookie_year': 2022,
        'rp_total': 167
    },
    {
        'team_key': '11111',
        'team_number': 11111,
        'team_name_short': 'Robo Warriors',
        'city': 'Guadalajara',
        'rookie_year': 2021,
        'rp_total': 132
    },
    {
        'team_key': '22222',
        'team_number': 22222,
        'team_name_short': 'Cyber Knights',
        'city': 'Puebla',
        'rookie_year': 2024,
        'rp_total': 98
    }
]

MOCK_TEAM_DETAILS = {
    '28254': {
        'awards': [
            {'award_name': 'Inspire Award'},
            {'award_name': 'Winning Alliance Captain'}
        ],
        'rankings': {'rp': 145, 'rank': 3}
    },
    '28255': {
        'awards': [
            {'award_name': 'Think Award'},
            {'award_name': 'Connect Award'}
        ],
        'rankings': {'rp': 167, 'rank': 1}
    },
    '11111': {
        'awards': [
            {'award_name': 'Design Award'}
        ],
        'rankings': {'rp': 132, 'rank': 5}
    },
    '22222': {
        'awards': [],
        'rankings': {'rp': 98, 'rank': 12}
    }
}

@app.route('/')
def index():
    return render_template('ftc.html')

@app.route('/api/ftc-mexico-data')
def get_ftc_mexico_data():
    """Obtiene eventos y equipos de México para la temporada actual"""
    try:
        if TOA_API_KEY:
            # Intentar obtener datos reales de TOA
            events_response = requests.get(
                f'{TOA_BASE_URL}/events',
                headers=TOA_HEADERS,
                params={'region_key': 'MX', 'season_key': '2425'}
            )
            
            teams_response = requests.get(
                f'{TOA_BASE_URL}/teams',
                headers=TOA_HEADERS,
                params={'region_key': 'MX'}
            )
            
            if events_response.status_code == 200 and teams_response.status_code == 200:
                events = events_response.json()
                teams = teams_response.json()
                
                return jsonify({
                    'status': 'success',
                    'source': 'live',
                    'events': events if events else MOCK_EVENTS,
                    'teams': teams if teams else MOCK_TEAMS
                })
        
        # Usar datos mock si no hay API key o falla la petición
        return jsonify({
            'status': 'success',
            'source': 'mock',
            'events': MOCK_EVENTS,
            'teams': MOCK_TEAMS
        })
        
    except Exception as e:
        # En caso de error, siempre devolver datos mock
        return jsonify({
            'status': 'success',
            'source': 'mock',
            'events': MOCK_EVENTS,
            'teams': MOCK_TEAMS,
            'error': str(e)
        })

@app.route('/api/team-detail/<team_key>')
def get_team_detail(team_key):
    """Obtiene detalles específicos de un equipo (premios y rankings)"""
    try:
        if TOA_API_KEY:
            # Intentar obtener datos reales
            awards_response = requests.get(
                f'{TOA_BASE_URL}/team/{team_key}/awards',
                headers=TOA_HEADERS
            )
            
            rankings_response = requests.get(
                f'{TOA_BASE_URL}/team/{team_key}/rankings/2425',
                headers=TOA_HEADERS
            )
            
            if awards_response.status_code == 200 and rankings_response.status_code == 200:
                awards = awards_response.json()
                rankings = rankings_response.json()
                
                return jsonify({
                    'status': 'success',
                    'source': 'live',
                    'awards': awards,
                    'rankings': rankings
                })
        
        # Usar datos mock
        if team_key in MOCK_TEAM_DETAILS:
            return jsonify({
                'status': 'success',
                'source': 'mock',
                **MOCK_TEAM_DETAILS[team_key]
            })
        else:
            return jsonify({
                'status': 'success',
                'source': 'mock',
                'awards': [],
                'rankings': {'rp': 0, 'rank': 0}
            })
            
    except Exception as e:
        # Datos mock en caso de error
        if team_key in MOCK_TEAM_DETAILS:
            return jsonify({
                'status': 'success',
                'source': 'mock',
                **MOCK_TEAM_DETAILS[team_key],
                'error': str(e)
            })
        else:
            return jsonify({
                'status': 'error',
                'message': str(e)
            })

@app.route('/api/nasa-rag', methods=['POST'])
def nasa_rag_chatbot():
    """Chatbot simulado que actúa como Juez Neutral experto en reglamento FTC"""
    data = request.json
    user_question = data.get('question', '').lower()
    
    # Respuestas predefinidas basadas en el reglamento FTC
    responses = {
        'puntos': 'En FTC DECODE, los puntos se otorgan por: colocar muestras en zonas (5-10 pts), ascender niveles (15-30 pts), y parkear en zonas seguras (5-15 pts). Los Ranking Points (RP) se calculan sumando puntos de clasificación + bonificaciones por premios.',
        'premios': 'Los premios principales son: Inspire Award (+15 RP bonus), Think Award (+10 RP), Connect Award (+10 RP), Innovate Award (+8 RP), Design Award (+8 RP), Control Award (+5 RP), Motivate Award (+5 RP), y Winning Alliance (+10 RP).',
        'clasificar': 'Para clasificar al siguiente nivel se necesitan típicamente más de 120 RP totales. Los equipos en la "Lista Verde" (clasificados retroactivos) avanzan automáticamente sin importar sus puntos actuales.',
        'robot': 'El robot debe caber en 18"x18"x18" al inicio. Puede expandirse durante el match. Debe usar componentes legales de FIRST y proveedores aprobados. El peso máximo es 42 lbs (19 kg).',
        'autonomo': 'El período autónomo dura 30 segundos. Los robots deben operar sin control humano. Se otorgan bonificaciones por: parkear correctamente, colocar muestras preconfiguradas, y completar navegación.',
        'teleop': 'El período TeleOperado dura 2 minutos. Los conductores controlan el robot manualmente. Se pueden manipular elementos de juego, ascender estructuras, y posicionar el robot para EndGame.',
        'endgame': 'Los últimos 30 segundos del TeleOp son EndGame. Se otorgan puntos extra por: ascender niveles de la estructura, parkear en zonas específicas, y completar tareas de cierre.',
        'falta': 'Las faltas incluyen: contacto destructivo con otros robots (Minor/Major), salirse del campo, interferir con elementos del oponente, y violar reglas de seguridad. Las Major Fouls dan puntos al oponente.'
    }
    
    # Buscar respuesta relevante
    response_text = 'Como Juez Neutral de FTC, te recomiendo consultar el Game Manual oficial para detalles específicos. ¿Tienes alguna pregunta sobre puntos, premios, clasificación, robot, autónomo, teleop, endgame o faltas?'
    
    for keyword, answer in responses.items():
        if keyword in user_question:
            response_text = f'⚖️ **Respuesta del Juez Neutral**: {answer}'
            break
    
    return jsonify({
        'status': 'success',
        'response': response_text,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
