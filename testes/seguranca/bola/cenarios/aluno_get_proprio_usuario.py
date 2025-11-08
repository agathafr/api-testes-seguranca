# testes/seguranca/bola/cenarios/aluno_get_proprio_usuario.py
from datetime import datetime
import requests, json
from pathlib import Path

URL = "http://127.0.0.1:5000"
login_data = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}  # Aluno A

ses = requests.Session()
login = ses.post(f"{URL}/login", json=login_data)

Path("respostas/bola/cenarios/aluno_get_proprio_usuario").mkdir(parents=True, exist_ok=True)
out = Path("respostas/bola/cenarios/aluno_get_proprio_usuario/aluno_get_proprio_usuario.txt")
with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login.status_code}\n")
    try:
        f.write("LOGIN body (json):\n" + json.dumps(login.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("LOGIN body (texto):\n" + login.text + "\n")

    meu_id = login.json().get("id")
    r = ses.get(f"{URL}/pessoas/{meu_id}")
    f.write(f"\nGET /pessoas/{meu_id} => {r.status_code}\n")
    try:
        f.write("RESPOSTA (json):\n" + json.dumps(r.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("RESPOSTA (texto):\n" + r.text + "\n")

print("Feito.")
