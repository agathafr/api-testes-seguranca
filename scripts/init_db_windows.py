from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import routes
from models import Pessoa
from database import db

with routes.app.app_context():
    db.create_all()
    print("✅ Tabelas criadas/validadas em pessoas.db")
