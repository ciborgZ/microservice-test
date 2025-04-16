from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, datetime
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
SECRET_KEY = 'sua_chave_secreta'

@app.route('/login', methods=['POST']) 
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    try:
        response = requests.post(
            'http://localhost:5001/users/email',
            json={'email': data['email']}
        )
    except requests.exceptions.ConnectionError:
        return jsonify({'mensagem': 'Erro ao conectar ao serviço de usuários'}), 500

    if response.status_code != 200:
        return jsonify({'mensagem': 'Usuario inválido'}), 401 # Enumeração de usuários

    usuario = response.json()

    if data['password'] != usuario['password']:  # Apenas para testes
        return jsonify({'mensagem': 'Senha inválida'}), 401 # Enumeração de usuários

    token = jwt.encode({
        'usuario_id': usuario['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token}), 200

@app.route('/verify', methods=['POST'])
def validate_token():
    token = request.headers.get('Authorization')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'valido': True, 'usuario_id': payload['usuario_id']})
    except jwt.ExpiredSignatureError:
        return jsonify({'mensagem': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'mensagem': 'Token inválido'}), 401

if __name__ == '__main__':
    app.run(port=5002, debug=True)