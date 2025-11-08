# testes/seguranca/bola/cenarios/aluno_get_outro_usuario.py
from datetime import datetime
import requests, json
from pathlib import Path

URL = "http://127.0.0.1:5000"
login_data = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}  # Aluno A

ses = requests.Session()
login = ses.post(f"{URL}/login", json=login_data)

# pega meu_id do corpo do login
try:
    meu_id = login.json().get("id")
except Exception:
    meu_id = None

# escolhe um id diferente do meu: usa 1, se for o meu usa 2
alvo_id = 1 if meu_id != 1 else 2

# (opcional) log no terminal para conferência
print(f"[DEBUG] meu_id={meu_id} | alvo_id={alvo_id} (terceiros? {alvo_id != meu_id})")

Path("respostas/bola/cenarios/aluno_get_outro_usuario").mkdir(parents=True, exist_ok=True)
out = Path("respostas/bola/cenarios/aluno_get_outro_usuario/aluno_get_outro_usuario.txt")
with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login.status_code}\n")
    try:
        f.write("LOGIN body (json):\n" + json.dumps(login.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("LOGIN body (texto):\n" + login.text + "\n")

    r = ses.get(f"{URL}/pessoas/{alvo_id}")
    f.write(f"\nGET /pessoas/{alvo_id} => {r.status_code}\n")
    try:
        f.write("RESPOSTA (json):\n" + json.dumps(r.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("RESPOSTA (texto):\n" + r.text + "\n")

print("Feito. (Se 200 com dados de terceiros, BOLA confirmada.)")
