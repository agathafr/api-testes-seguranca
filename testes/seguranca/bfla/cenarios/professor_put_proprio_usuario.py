# testes/seguranca/bfla/cenarios/professor_put_proprio_usuario.py
from datetime import datetime
from pathlib import Path
import requests
import sys

URL = "http://127.0.0.1:5000"

# login do professor (corrigido para @sga)
login_data = {"login": "377539@sga.pucminas.br", "senha": "377539"}

# pasta de evidências
out_dir = Path("respostas/bfla/cenarios/professor_put_proprio_usuario")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "professor_put_proprio_usuario.txt"

ses = requests.Session()

with out_file.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")

    # 1) Login como professor
    login_resp = ses.post(f"{URL}/login", json=login_data)
    f.write(f"LOGIN status: {login_resp.status_code}\n")
    try:
        f.write(f"LOGIN body (json): {login_resp.json()}\n")
    except Exception:
        f.write(f"LOGIN body (text): {login_resp.text}\n")

    if login_resp.status_code != 200:
        f.write("Login falhou — encerrando cenário para evitar falso negativo.\n")
        sys.exit(1)

    prof_id = login_resp.json().get("id")

    # 2) PUT no próprio ID (controle positivo: deve ser permitido)
    put_payload = {
        # não alteramos 'perfil' (mantém Professor); mudamos apenas o nome
        "nome": "Professor — atualização de controle (próprio)",
        # manter login igual para não quebrar próximos testes
        "login": login_resp.json().get("login"),
    }

    put_resp = ses.put(f"{URL}/pessoas/{prof_id}", json=put_payload)
    f.write(f"PUT /pessoas/{prof_id} status: {put_resp.status_code}\n")
    try:
        f.write(f"PUT body (json): {put_resp.json()}\n")
    except Exception:
        f.write(f"PUT body (text): {put_resp.text}\n")

print("Feito. Evidência em:", out_file)
