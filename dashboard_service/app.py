from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if request.method == 'OPTIONS':
        return '', 200 

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'mensagem': 'Token não enviado'}), 401

    # Validação do token via auth_service
    response = requests.post('http://localhost:5002/verify', headers={'Authorization': token})
    if response.status_code == 200:
        dados = response.json()
        return render_template('dashboard.html')
    else:
        return '<h1>nao logado</h1>'

if __name__ == '__main__':
    app.run(port=5003, debug=True)