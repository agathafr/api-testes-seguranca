from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
import csv

# Configuração do banco de dados
db = SQLAlchemy()

# Defina o modelo aqui mesmo
class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    perfil = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)

def init_db():
    # Configuração temporária do Flask
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pessoas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        if Pessoa.query.count() == 0:
            with open('listagem.csv', 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=';')
                
                for row in csv_reader:
                    pessoa = Pessoa(
                        nome=row['Nome'],
                        login=row['Login'],
                        senha=row['Senha'],
                        perfil=row['Perfil'],
                        status=row['Status']
                    )
                    db.session.add(pessoa)
            
            db.session.commit()
            print(f"✅ Banco de dados populado com {Pessoa.query.count()} registros!")
        else:
            print("ℹ️ O banco de dados já contém registros. Nada foi alterado.")

if __name__ == '__main__':
    init_db()