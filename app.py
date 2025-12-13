import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Configuración de la API Key (la toma de Heroku)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Función para cargar tu archivo de conocimiento
def cargar_conocimiento():
    try:
        with open('conocimiento.json', 'r', encoding='utf-8') as f:
            return f.read() # Lo leemos como texto para pasárselo a la IA
    except Exception as e:
        print(f"Error cargando conocimiento: {e}")
        return "No hay información adicional disponible."

# Cargamos el cerebro al iniciar
base_de_conocimiento = cargar_conocimiento()

@app.route("/")
def index():
    # Busca el archivo index.html dentro de la carpeta templates
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    
    # --- AQUÍ ESTÁ LA MAGIA BILINGÜE ---
    # Instrucciones para la IA
    system_instruction = f"""
    Eres un asistente inteligente y útil para el Proyecto Aztlán.
    
    Tus conocimientos base son estos:
    {base_de_conocimiento}
    
    INSTRUCCIONES CLAVE:
    1. Usa la información de arriba para responder.
    2. Si no sabes la respuesta, di que no tienes esa información por ahora.
    3. IMPORTANTE: Si el usuario escribe en ESPAÑOL, responde en ESPAÑOL.
    4. IMPORTANTE: Si el usuario escribe en INGLÉS (English), responde en INGLÉS.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192", # Un modelo rápido y bueno
            temperature=0.7,
        )
        
        bot_response = chat_completion.choices[0].message.content
        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"response": f"Lo siento, hubo un error de conexión: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
