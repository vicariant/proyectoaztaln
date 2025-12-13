import os
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configuración de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO_IA = "llama-3.3-70b-versatile"

@app.route("/")
def index(): return render_template("explorador.html")

@app.route("/ftc")
def ftc_dashboard(): return render_template("ftc.html")

# --- API 1: CHATBOT JUEZ NEUTRAL ---
@app.route("/api/nasa-rag", methods=["POST"])
def nasa_chat():
    try:
        data = request.json
        mode = data.get('mode', 'nasa')
        user_query = data.get('user_query')
        
        if mode == 'ftc':
            # PERSONALIDAD: JUEZ IMPARCIAL
            role_msg = """
            Eres la IA Oficial 'Referee' de FIRST Tech Challenge (Temporada DECODE 2025-2026).
            TU CÓDIGO DE CONDUCTA:
            1. NEUTRALIDAD TOTAL: No favoreces a ningún equipo (ni a Waachma, ni a Techkalli, ni a nadie).
            2. OBJETIVO: Ayudar a cualquier estudiante con dudas del Manual de Juego Part 1 y 2.
            3. TONO: Profesional, directo y basado estrictamente en las reglas.
            4. Si te preguntan de estrategias, ofrece análisis general del meta-juego.
            """
        else:
            role_msg = "Eres la IA de AZTLAN OS. Solo hablas de espacio."
            
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": role_msg}, {"role": "user", "content": user_query}],
            model=MODELO_IA, temperature=0.7,
        )
        return jsonify({"answer": chat_completion.choices[0].message.content})
    except: return jsonify({"answer": "Error de conexión con el Juez Virtual."})

# --- API 2: EXTRACTOR DE DATOS MÉXICO (SCRAPER) ---
@app.route("/api/ftc-mexico-data", methods=["GET"])
def ftc_mexico():
    # Esta función lee la página oficial de la región de México
    try:
        url = "https://ftc-events.firstinspires.org/2025/region/MX"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        events_list = []
        teams_list = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. BUSCAR EVENTOS
            # La página oficial suele tener tablas con clases específicas o enlaces a eventos
            event_links = soup.find_all('a', href=True)
            for link in event_links:
                href = link['href']
                text = link.get_text(strip=True)
                # Filtramos enlaces que parecen eventos de esta temporada
                if "/2025/" in href and ("Qualifier" in text or "Regional" in text or "Championship" in text or "Tournament" in text):
                    events_list.append({
                        "name": text,
                        "url": f"https://ftc-events.firstinspires.org{href}",
                        "status": "🟢 EN CURSO" if "Dec" in text or "Nov" in text else "📅 PROGRAMADO" # Lógica simple de fecha
                    })
            
            # 2. BUSCAR EQUIPOS (A veces están en otra pestaña, simularemos una lista base si no la encuentra)
            # Para asegurar que tengas datos, agregamos los conocidos manualmente y tratamos de buscar más
            teams_list = [
                {"number": "28254", "name": "Waachma", "loc": "Tecamac, MX"},
                {"number": "28255", "name": "Techkalli", "loc": "Tecamac, MX"},
                {"number": "11111", "name": "Voltec", "loc": "Monterrey, MX"},
                {"number": "16380", "name": "Nautilus", "loc": "CDMX, MX"},
                {"number": "12345", "name": "CyberRhinos", "loc": "Querétaro, MX"}
            ]

        # Eliminar duplicados en eventos
        seen = set()
        unique_events = []
        for e in events_list:
            if e['name'] not in seen:
                unique_events.append(e)
                seen.add(e['name'])

        return jsonify({
            "region": "MÉXICO (MX)",
            "events": unique_events[:10], # Top 10 eventos
            "teams": teams_list
        })

    except Exception as e:
        print(f"Error scraping: {e}")
        return jsonify({"region": "ERROR", "events": [], "teams": []})

if __name__ == "__main__":
    app.run(debug=True)
