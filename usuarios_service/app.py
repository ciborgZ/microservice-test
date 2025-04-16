from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()

## Middleware
def validate_token():
    token = request.headers.get('Authorization')
    if not token:
        return None

    response = requests.post(
        'http://localhost:5002/verify',
        headers={'Authorization': token}
    )

    if response.status_code == 200:
        return response.json()['usuario_id']
    return None



## Cadastrar novo usuario
@app.route('/users/create', methods=['POST'])
def create_users():
    if request.method == 'OPTIONS':
        return '', 200 
    data = request.json

    user_exists = User.query.filter_by(email=data['email']).first() ## Enumeração de usuários
    if user_exists:
        return jsonify({'mensagem': 'E-mail já cadastrado'}), 400

    new_user = User(name=data['name'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado com sucesso'}), 201


@app.route('/users/all', methods=['GET']) ## Isso aqui deveria ser considerado como vuln (possibilidade de listar todos os usuários da aplicação)
def get_all_users():
    token_is_valid = validate_token()
    if not token_is_valid:
        return jsonify({'mensagem': 'Acesso não autorizado'}), 401
    
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])
    

@app.route('/users/email', methods=['POST']) ## Enumeração de usuários sob demanda
def get_user_by_email():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'mensagem': 'Email não fornecido'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404

    return jsonify({
        'id': user.id,
        'nome': user.name,
        'email': user.email,
        'password': user.password
    }), 200


@app.route('/users/me', methods=['GET']) ## Enumeração de usuários sob demanda
def get_user_data():

    user_id = validate_token()
    if not user_id:
        return jsonify({'mensagem': 'Acesso não autorizado'}), 401


    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404

    return jsonify({
        'id': user.id,
        'nome': user.name,
        'email': user.email,
        'password': user.password
    }), 200


@app.route('/users/update/<int:id>', methods=['PUT']) ## Possibilidade de alterar o e-mail de qualquer usuário (IDOR clássico que permite account takeover)
def update_users(id):
    data = request.json
    user = User.query.get_or_404(id)
    user.name = data['nome']
    user.email = data['email']
    db.session.commit()
    return jsonify({'mensagem': 'Usuário atualizado'}) 

@app.route('/users/<int:id>', methods=['DELETE']) ## Preciso estar autenticado, mas posso deletar contas de outros usuários
def remove_users(id):
    token_is_valid = validate_token()
    if not token_is_valid:
        return jsonify({'mensagem': 'Acesso não autorizado'}), 401
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário deletado'})

if __name__ == '__main__':
    app.run(port=5001, debug=True)