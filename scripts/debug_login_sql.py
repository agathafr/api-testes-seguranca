# app/debug_login_sql.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import routes
from database import db

login  = "1566256@sga.pucminas.br"
senha  = "1566256"

query_full = f"SELECT * FROM pessoa WHERE Login = '{login}' AND Senha = '{senha}'"
query_login_only = f"SELECT * FROM pessoa WHERE Login = '{login}'"

with routes.app.app_context():
    conn = db.engine.raw_connection()
    cur = conn.cursor()

    print(">> QUERY (login+senha):", query_full)
    cur.execute(query_full)
    row = cur.fetchone()
    print("RESULT (login+senha):", row)

    print("\n>> QUERY (apenas login):", query_login_only)
    cur.execute(query_login_only)
    row2 = cur.fetchone()
    print("RESULT (apenas login):", row2)

    cur.close()
    conn.close()
