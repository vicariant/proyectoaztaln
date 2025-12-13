import os
import requests
import random
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
from bs4 import BeautifulSoup # Herramienta de extracción

app = Flask(__name__)

# Configuración de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index(): return render_template("explorador.html")

@app.route("/ftc")
def ftc_dashboard(): return render_template("ftc.html")

# --- API 1: CHATBOT NEUTRAL ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        mode = data.get('mode', 'nasa')
        user_query = data.get('user_query')
        
        if mode == 'ftc':
            role_msg = "Eres la IA Juez de FIRST Tech Challenge 2025-2026 (DECODE). Eres experto en el reglamento, neutral y ayudas a todos los equipos. Respuestas breves y técnicas."
        else:
            role_msg = "Eres la IA de AZTLAN OS. Solo hablas de espacio y ciencia ficción."
            
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
    except: return jsonify({"answer": "Error de conexión."})

# --- API 2: EXTRACTOR DE EVENTOS (SCRAPER) ---
@app.route("/api/ftc-live-scrape", methods=["GET"])
def ftc_live():
    # 1. Intentamos extraer datos reales de la web oficial
    try:
        # URL oficial de eventos
        url = "https://ftc-events.firstinspires.org/2025/events"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            events = []
            
            # Buscamos la tabla de eventos (la estructura suele ser table rows)
            # NOTA: Esto es una búsqueda general, filtraremos por "Mexico"
            for row in soup.find_all('tr'):
                text = row.get_text()
                # Filtramos eventos que parezcan de México o relevantes
                if "Mexico" in text or "Regional" in text or "MX" in text:
                    cols = row.find_all('td')
                    if len(cols) > 2:
                        events.append({
                            "name": cols[0].get_text(strip=True),
                            "location": cols[1].get_text(strip=True),
                            "date": cols[2].get_text(strip=True),
                            "status": "En Curso" if "Dec" in cols[2].get_text() else "Programado"
                        })
            
            if events:
                return jsonify({"source": "LIVE_SCRAPE", "data": events})
                
    except Exception as e:
        print(f"Error scraping: {e}")

    # 2. DATOS DE RESPALDO (Si el scraper falla o no hay eventos listados aún)
    # Simulamos EXACTAMENTE los 2 torneos de hoy que mencionaste
    fallback_data = [
        {
            "name": "DECODE Regional CDMX",
            "location": "Ciudad de México, MX",
            "date": "Dec 13, 2025",
            "status": "🟢 EN VIVO",
            "teams_count": 24
        },
        {
            "name": "DECODE Bajío Tournament",
            "location": "Querétaro, MX",
            "date": "Dec 13, 2025",
            "status": "🟢 EN VIVO",
            "teams_count": 18
        },
        {
            "name": "Qualifying Tournament",
            "location": "Monterrey, MX",
            "date": "Jan 10, 2026",
            "status": "📅 Próximo",
            "teams_count": 30
        }
    ]
    return jsonify({"source": "BACKUP_SYSTEM", "data": fallback_data})

if __name__ == "__main__":
    app.run(debug=True)
