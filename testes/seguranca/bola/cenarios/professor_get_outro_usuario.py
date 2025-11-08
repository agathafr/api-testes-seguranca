# testes/seguranca/bola/cenarios/professor_get_outro_usuario.py
from datetime import datetime
import requests
from pathlib import Path
import json

URL = "http://127.0.0.1:5000"
login_data = {"login": "377539@sga.pucminas.br", "senha": "377539"}  # Professor
alvo_id = 2  # outro usuário (ex.: Aluno B)

ses = requests.Session()

# 1) Login
login = ses.post(f"{URL}/login", json=login_data)

# 2) Evita “falso negativo”: garante que alvo_id != id do usuário logado
try:
    meu_id = login.json().get("id")
except Exception:
    meu_id = None

if meu_id is not None and alvo_id == meu_id:
    # escolhe um ID diferente do meu
    alvo_id = 1 if meu_id != 1 else 3

# (opcional) evidência de que pedimos dados de terceiros
print(f"[DEBUG] meu_id={meu_id} | alvo_id={alvo_id} (terceiros? {alvo_id != meu_id})")

# 3) Pasta/arquivo de evidência
Path("respostas/bola/cenarios/professor_get_outro_usuario").mkdir(parents=True, exist_ok=True)
out = Path("respostas/bola/cenarios/professor_get_outro_usuario/professor_get_outro_usuario.txt")

with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login.status_code}\n")
    try:
        f.write(f"LOGIN body:\n{json.dumps(login.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"LOGIN body (texto):\n{login.text}\n")

    # 4) Tentativa de ler dados de outro usuário
    r = ses.get(f"{URL}/pessoas/{alvo_id}")
    f.write(f"\nGET /pessoas/{alvo_id} => {r.status_code}\n")
    try:
        f.write(f"RESPOSTA:\n{json.dumps(r.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"RESPOSTA (texto):\n{r.text}\n")

print("Feito. (Se 200 com dados de terceiros, BOLA confirmada.)")
