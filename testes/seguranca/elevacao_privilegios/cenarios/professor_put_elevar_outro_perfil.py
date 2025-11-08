# testes/seguranca/elevacao_privilegios/cenarios/professor_put_elevar_outro_perfil.py
from datetime import datetime
import requests, json
from pathlib import Path

URL = "http://127.0.0.1:5000"

# Credenciais do professor (id 19 nos dumps)
login_data = {"login": "377539@sga.pucminas.br", "senha": "377539"}  # Professor

# alvo padrão: um aluno qualquer diferente do professor (ex.: id=2)
alvo_id = 2

ses = requests.Session()

# 1) login
login = ses.post(f"{URL}/login", json=login_data)

# pega meu_id para garantir que não alteraremos o próprio perfil
try:
    meu_id = login.json().get("id")
except Exception:
    meu_id = None

# se por acaso o alvo for eu mesmo, muda para outro id de aluno
if meu_id is not None and alvo_id == meu_id:
    alvo_id = 1 if meu_id != 1 else 3

# 2) registrar evidência
out_dir = Path("respostas/elevacao_privilegios/cenarios/professor_put_elevar_outro_perfil")
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "professor_put_elevar_outro_perfil.txt"

with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login.status_code}\n")
    try:
        f.write(f"LOGIN body (json):\n{json.dumps(login.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"LOGIN body (texto):\n{login.text}\n")

    # 3) tentativa de elevação: professor altera PERFIL de OUTRO usuário para 'Professor'
    payload = {"perfil": "Professor"}  # alvo vai virar Professor
    r = ses.put(f"{URL}/pessoas/{alvo_id}", json=payload)
    f.write(f"\nPUT /pessoas/{alvo_id} => {r.status_code}\n")

    try:
        f.write(f"RESPOSTA (json):\n{json.dumps(r.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"RESPOSTA (texto):\n{r.text}\n")

print("Feito. (Se 200 e o perfil do alvo mudar para 'Professor', elevação por OUTRO usuário foi permitida.)")
