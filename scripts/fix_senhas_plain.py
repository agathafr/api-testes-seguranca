# scripts/fix_senhas_plain.py
import sys
from pathlib import Path

# Garante que o Python enxergue o módulo "app"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from models import Pessoa
import routes

with routes.app.app_context():
    pessoas = Pessoa.query.all()
    for p in pessoas:
        if len(p.senha) > 10:  # provavel hash
            # simplifica a senha para os 6 primeiros dígitos do login (antes do @)
            p.senha = p.login.split("@")[0][-6:]
            print(f"Ajustando senha para {p.login} -> {p.senha}")
    routes.db.session.commit()

print("Senhas normalizadas.")
