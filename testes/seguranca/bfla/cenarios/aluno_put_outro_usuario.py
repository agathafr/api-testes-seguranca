# testes/seguranca/bfla/cenarios/aluno_put_outro_usuario.py
from datetime import datetime
from pathlib import Path
import requests
import json

URL = "http://127.0.0.1:5000"

# 1) Login como ALUNO (id=1 no seu banco)
login_data = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}  # Aluno
ses = requests.Session()
login_resp = ses.post(f"{URL}/login", json=login_data)

# 2) Tentar atualizar OUTRO usuário (ex.: id=2)
target_id = 2
put_payload = {
    "nome": "Tentativa indevida de edição",
    "perfil": "Administrador"  # qualquer alteração aqui serve; o foco é ser OUTRO usuário
}
put_resp = ses.put(f"{URL}/pessoas/{target_id}", json=put_payload)

# 3) Salvar evidências
out_dir = Path("respostas/bfla/cenarios/aluno_put_outro_usuario")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "aluno_put_outro_usuario.txt"

with out_file.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login_resp.status_code}\n")
    try:
        f.write("LOGIN body (json):\n")
        f.write(json.dumps(login_resp.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("LOGIN body (text):\n" + login_resp.text + "\n")

    f.write(f"\nPUT /pessoas/{target_id} status: {put_resp.status_code}\n")
    try:
        f.write("PUT body (json):\n")
        f.write(json.dumps(put_resp.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("PUT body (text):\n" + put_resp.text + "\n")

print("Feito. Evidência salva em respostas/bfla/cenarios/aluno_put_outro_usuario/aluno_put_outro_usuario.txt")
