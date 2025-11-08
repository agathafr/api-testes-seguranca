# testes/seguranca/elevacao_privilegios/cenarios/aluno_put_elevar_outro_perfil.py
from datetime import datetime
import requests
from pathlib import Path
import json

URL = "http://127.0.0.1:5000"

# Login como Aluno A
login_data = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}  # Aluno A

ses = requests.Session()
login = ses.post(f"{URL}/login", json=login_data)

# Decide um alvo diferente do próprio usuário logado
try:
    meu_id = login.json().get("id")
except Exception:
    meu_id = None

alvo_id = 2  # candidato padrão
if meu_id is not None and alvo_id == meu_id:
    alvo_id = 3  # garante que é “outro” usuário

# Pasta/arquivo de evidência
out_dir = Path("respostas/elevacao_privilegios/cenarios/aluno_put_elevar_outro_perfil").mkdir(parents=True, exist_ok=True)
out_path = Path("respostas/elevacao_privilegios/cenarios/aluno_put_elevar_outro_perfil/aluno_put_elevar_outro_perfil.txt")

with out_path.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login.status_code}\n")
    try:
        f.write(f"LOGIN body (json):\n{json.dumps(login.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"LOGIN body (texto):\n{login.text}\n")

    # Tenta elevar o perfil de OUTRO usuário para 'Professor'
    payload = {"perfil": "Professor"}
    r = ses.put(f"{URL}/pessoas/{alvo_id}", json=payload)

    f.write(f"\nPUT /pessoas/{alvo_id} com corpo {payload} => {r.status_code}\n")
    try:
        f.write(f"RESPOSTA (json):\n{json.dumps(r.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"RESPOSTA (texto):\n{r.text}\n")

print("Feito. (Se voltar 200 e o perfil do alvo virar 'Professor', elevação de privilégio em OUTRO usuário confirmada.)")
