# app/fix_senhas_plain.py
from pathlib import Path
import sys, csv
sys.path.insert(0, str(Path(__file__).resolve().parent))

import routes
from models import Pessoa
from database import db

csv_path = Path(__file__).resolve().parent / "listagem.csv"

with routes.app.app_context():
    atualizados = 0
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            p = Pessoa.query.filter_by(login=row["Login"]).first()
            if p and p.senha != row["Senha"]:
                p.senha = row["Senha"]           # << sem hash, texto puro
                db.session.add(p)
                atualizados += 1
    db.session.commit()
    print(f"Senhas ajustadas para texto puro. Registros atualizados: {atualizados}")
