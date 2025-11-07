from pathlib import Path
import sys, csv
sys.path.insert(0, str(Path(__file__).resolve().parent))

from werkzeug.security import generate_password_hash
import routes
from models import Pessoa
from database import db

CSV_PATH = Path(__file__).resolve().parent / "listagem.csv"

with routes.app.app_context():
    total_antes = Pessoa.query.count()
    inseridos = 0

    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # evita duplicar pelo login
            if Pessoa.query.filter_by(login=row["Login"]).first():
                continue

            p = Pessoa(
                nome=row["Nome"],
                login=row["Login"],
                senha=generate_password_hash(row["Senha"]),
                perfil=row["Perfil"],
                status=row["Status"]
            )
            db.session.add(p)
            inseridos += 1

    db.session.commit()
    print(f"✅ Importação concluída. Antes: {total_antes} | Inseridos agora: {inseridos} | Total: {Pessoa.query.count()}")
