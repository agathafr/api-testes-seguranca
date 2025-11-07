from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent))

import routes
from database import db

with routes.app.app_context():
    print("cwd:", os.getcwd())
    print("db url:", db.engine.url)
