from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai

app = Flask(__name__)

UNSPLASH_ACCESS_KEY = ''
GEMINI_API_KEY = ''
GEMINI_MODEL_NAME = 'gemini-2.0-flash'  

genai.configure(api_key=GEMINI_API_KEY);

@app.route('/searchImages/unsplash', methods=['POST'])
def search_unsplash():
    query = request.json.get('query')

    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400

    url = f'https://api.unsplash.com/search/photos'
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
    params = {'query': query, 'per_page': 10}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() 
        data = response.json()
        images = [result['urls']['small'] for result in data['results']] 
        return jsonify({'images': images})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro ao buscar imagens no Unsplash: {str(e)}'}), 500

def generate_gemini_response(user_input):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        prompt = f"""
        Você é um assistente virtual especializado em ajudar.
        
        Pergunta do usuário: {user_input}
        
        Resposta:
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0, 
                max_output_tokens=200,  
            )
        )

        if not response.text:
            return "Informação não encontrada em nossos registros."
        
        return response.text
    except Exception as e:
        return f"Erro no sistema: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat_gemini():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'Mensagem não fornecida'}), 400

    response_message = generate_gemini_response(user_message)

    return jsonify({'chat_history': [{'message': response_message}]})

@app.route("/")
def home():
    return render_template("index.html", chat_history=[])

if __name__ == "__main__":
    app.run(debug=True)
