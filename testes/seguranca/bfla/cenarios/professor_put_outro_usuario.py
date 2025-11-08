# testes/seguranca/bfla/cenarios/professor_put_outro_usuario.py
from datetime import datetime
from pathlib import Path
import requests
import json

URL = "http://127.0.0.1:5000"

# 1) Login como professor — exatamente como no login_test.py (Session + json)
login_payload = {"login": "377539@sga.pucminas.br", "senha": "377539"}
ses = requests.Session()
login_resp = ses.post(f"{URL}/login", json=login_payload)

# pasta de evidência
out_dir = Path("respostas/bfla/cenarios/professor_put_outro_usuario")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "professor_put_outro_usuario.txt"

# sempre registre a tentativa de login
with out_file.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login_resp.status_code}\n")
    try:
        f.write("LOGIN body (json):\n")
        f.write(json.dumps(login_resp.json(), ensure_ascii=False, indent=2))
        f.write("\n")
    except Exception:
        f.write("LOGIN body (text):\n")
        f.write(login_resp.text + "\n")

# se o login falhar, encerramos para evitar falso negativo
if login_resp.status_code != 200:
    print("Login falhou no cenário. Evidência registrada.")
    raise SystemExit(1)

# 2) PUT tentando editar outro usuário (aluno id=1) usando a MESMA sessão
target_id = 1
put_payload = {
    "nome": "Usuário alterado indevidamente",
    "perfil": "Administrador"
}

put_resp = ses.put(f"{URL}/pessoas/{target_id}", json=put_payload)

# 3) Registrar evidência do PUT
with out_file.open("a", encoding="utf-8") as f:
    f.write(f"\nPUT /pessoas/{target_id} status: {put_resp.status_code}\n")
    try:
        f.write("PUT body (json):\n")
        f.write(json.dumps(put_resp.json(), ensure_ascii=False, indent=2))
        f.write("\n")
    except Exception:
        f.write("PUT body (text):\n")
        f.write(put_resp.text + "\n")

print("Feito. Evidência salva em", out_file)
