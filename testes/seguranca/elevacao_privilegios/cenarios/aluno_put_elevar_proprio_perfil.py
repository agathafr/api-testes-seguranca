# testes/seguranca/elevacao_privilegios/cenarios/aluno_put_elevar_proprio_perfil.py
from datetime import datetime
from pathlib import Path
import requests
import json

URL = "http://127.0.0.1:5000"

# Aluno A (id = 1)
login_data = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}
aluno_id = 1

# pasta de evidência
out_dir = Path("respostas/elevacao_privilegios/cenarios/aluno_put_elevar_proprio_perfil")
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "aluno_put_elevar_proprio_perfil.txt"

with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")

    # 1) Login como aluno
    ses = requests.Session()
    login = ses.post(f"{URL}/login", json=login_data)
    f.write(f"LOGIN status: {login.status_code}\n")
    try:
        f.write(f"LOGIN body (json):\n{json.dumps(login.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"LOGIN body (texto):\n{login.text}\n")

    # 2) Tentativa de elevação de privilégio no próprio registro
    payload = {"perfil": "Professor"}
    r = ses.put(f"{URL}/pessoas/{aluno_id}", json=payload)
    f.write(f"\nPUT /pessoas/{aluno_id} (elevar para 'Professor') => {r.status_code}\n")
    try:
        f.write(f"RESPOSTA (json):\n{json.dumps(r.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"RESPOSTA (texto):\n{r.text}\n")

print("Feito. Evidência em respostas/elevacao_privilegios/cenarios/aluno_put_elevar_proprio_perfil/aluno_put_elevar_proprio_perfil.txt")
