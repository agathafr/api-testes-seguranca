# testes/seguranca/bfla/cenarios/aluno_put_proprio_usuario.py
from datetime import datetime
import requests
from pathlib import Path
import json

URL = "http://127.0.0.1:5000"

# 1) Login como ALUNO (id 1)
login_data = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}  # Aluno
ses = requests.Session()
login_resp = ses.post(f"{URL}/login", json=login_data)

# pasta de evidência
out_dir = Path("respostas/bfla/cenarios/aluno_put_proprio_usuario")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "aluno_put_proprio_usuario.txt"

with out_file.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"LOGIN status: {login_resp.status_code}\n")
    try:
        f.write("LOGIN body (json):\n")
        f.write(json.dumps(login_resp.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("LOGIN body (text):\n")
        f.write(login_resp.text + "\n")

    # Se o login falhar, encerramos (evita falso negativo)
    if login_resp.status_code != 200:
        f.write("Login falhou no cenário. Evidência registrada.\n")
        raise SystemExit(1)

    # 2) PUT atualizando o próprio usuário (aluno id=1) usando a MESMA sessão
    target_id = 1
    put_payload = {
        "nome": "Aluno - atualização BFLA",
        # NÃO alteramos 'perfil' (continua Aluno) para não misturar com elevação
        # Poderíamos alterar também 'login' ou 'senha', mas mantemos simples aqui.
    }

    put_resp = ses.put(f"{URL}/pessoas/{target_id}", json=put_payload)

    f.write(f"\nPUT /pessoas/{target_id} status: {put_resp.status_code}\n")
    try:
        f.write("PUT body (json):\n")
        f.write(json.dumps(put_resp.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("PUT body (text):\n")
        f.write(put_resp.text + "\n")

print(f"Feito. Evidência em {out_file}")
