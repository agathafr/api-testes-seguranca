import os
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import Pessoa, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pessoas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Necessário para sessões
db.init_app(app)

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Acesso negado. Faça login primeiro."}), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar se o usuário é um administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = Pessoa.query.get(session['user_id'])
        if not user or user.perfil.lower() != 'professor':  # Assumindo que 'professor' é o perfil de admin
            return jsonify({"error": "Acesso negado. Permissão insuficiente."}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login', '')
    senha = data.get('senha', '')
    
    query = f"SELECT * FROM pessoa WHERE Login = '{login}' AND Senha = '{senha}'"
    print("DEBUG login(): login/senha ->", login, senha, flush=True)
    print("DEBUG login(): query ->", query, flush=True)
    print("DEBUG path: cwd =", os.getcwd(), flush=True)
    print("DEBUG db url:", db.engine.url, flush=True)
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    pessoa = cursor.fetchone()
    print("DEBUG login(): pessoa ->", pessoa, flush=True)
    cursor.close()
    connection.close()
    
    if pessoa:
        session['user_id'] = pessoa[0]
        return jsonify({
            "id": pessoa[0],
            "nome": pessoa[1],
            "login": pessoa[2],
            "perfil": pessoa[4]
        }), 200
    return jsonify({"error": "Login falhou"}), 401

@app.route('/pessoas/<int:pessoa_id>', methods=['GET'])
@login_required
def get_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    return jsonify(pessoa.to_dict())

@app.route('/pessoas/<int:pessoa_id>/ativar', methods=['POST'])
@login_required
@admin_required
def ativar_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    pessoa.status = "Ativo"
    db.session.commit()
    return jsonify({"message": "Usuário ativado"})

@app.route('/pessoas/<int:pessoa_id>/desativar', methods=['POST'])
@login_required
@admin_required
def desativar_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    pessoa.status = "Inativo"
    db.session.commit()
    return jsonify({"message": "Usuário desativado"})

@app.route('/pessoas/<int:pessoa_id>', methods=['PUT'])
@login_required
def update_pessoa(pessoa_id):
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    data = request.get_json()
    
    if session['user_id'] != pessoa.id and Pessoa.query.get(session['user_id']).perfil != 'professor':
        return jsonify({"error": "Acesso negado. Você só pode editar seu próprio perfil."}), 403
    
    if 'perfil' in data:
        pessoa.perfil = data['perfil']

    pessoa.nome = data.get('nome', pessoa.nome)
    pessoa.login = data.get('login', pessoa.login)
    
    if 'senha' in data:
        pessoa.senha = generate_password_hash(data['senha'])
    
    db.session.commit()
    return jsonify(pessoa.to_dict())

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout realizado com sucesso"})

if __name__ == '__main__':
    app.run(debug=True)