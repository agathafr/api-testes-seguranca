# create_db.py (na raiz do projeto)
from pathlib import Path
import sys

# adiciona a pasta app no caminho de importação
sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

import routes
from database import db

with routes.app.app_context():
    db.create_all()
    print("✅ Tabelas criadas em pessoas.db (na raiz do projeto)")
