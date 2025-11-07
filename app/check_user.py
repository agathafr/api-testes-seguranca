# app/check_user.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import routes
from models import Pessoa

login = "1566256@sga.pucminas.br"

with routes.app.app_context():
    p = Pessoa.query.filter_by(login=login).first()
    if not p:
        print("USUARIO NAO ENCONTRADO")
    else:
        print("Login:", p.login)
        print("Senha armazenada (campo senha):", p.senha)
        print("Perfil:", p.perfil)
        print("Status:", p.status)
