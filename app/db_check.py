# app/db_check.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import routes
from models import Pessoa

with routes.app.app_context():
    print("Total de pessoas:", Pessoa.query.count())
