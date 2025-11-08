# testes/seguranca/bfla/cenarios/post_desativar_outro_usuario.py
"""
BFLA: autenticar como Aluno e tentar executar POST /pessoas/<id>/desativar em outros IDs.
Saída: respostas\bfla\cenarios\post_desativar_outro_usuario\post_desativar_outro_usuario.txt
"""
import os
import json
import requests
from datetime import datetime

BASE = "http://127.0.0.1:5000"

# Credenciais de baixo privilégio (Aluno) — ajuste se necessário
ALUNO_LOGIN = "1566256@sga.pucminas.br"
ALUNO_SENHA  = "1566256"

# IDs alvo (outros usuários)
TARGET_IDS = [2, 3, 19]

out_dir = os.path.join("respostas", "bfla", "cenarios", "post_desativar_outro_usuario")
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "post_desativar_outro_usuario.txt")

s = requests.Session()

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return resp.text

results = []
results.append({"meta": {
    "executed_at": datetime.utcnow().isoformat() + "Z",
    "base": BASE,
    "note": "Autenticado como Aluno; testar POST /pessoas/<id>/desativar em outros ids (BFLA)."
}})

# 1) Login como Aluno
try:
    r = s.post(f"{BASE.rstrip('/')}/login", json={"login": ALUNO_LOGIN, "senha": ALUNO_SENHA}, timeout=8)
    login_ok = (r.status_code == 200)
    results.append({
        "phase": "login",
        "status_code": r.status_code,
        "headers": dict(r.headers),
        "body": safe_json(r)
    })
except Exception as e:
    login_ok = False
    results.append({"phase": "login", "error": str(e)})

if not login_ok:
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("LOGIN_FAILED\n")
        f.write(json.dumps(results, ensure_ascii=False, indent=2))
    print("Feito")
    raise SystemExit("Login falhou — ver arquivo de saída.")

# 2) POST /pessoas/<id>/desativar para cada target
for tid in TARGET_IDS:
    url = f"{BASE.rstrip('/')}/pessoas/{tid}/desativar"
    try:
        resp = s.post(url, timeout=8)
        results.append({
            "scenario": "post_desativar_as_aluno",
            "id": tid,
            "url": url,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "body": safe_json(resp)
        })
    except Exception as e:
        results.append({
            "scenario": "post_desativar_as_aluno",
            "id": tid,
            "url": url,
            "error": str(e)
        })

# 3) Grava resultados
with open(out_file, "w", encoding="utf-8") as f:
    f.write("BFLA - post_desativar_outro_usuario (autenticado como Aluno)\n\n")
    for item in results:
        f.write("----\n")
        if item.get("phase") == "login":
            f.write("PHASE: LOGIN\n")
            f.write(f"STATUS_CODE: {item.get('status_code')}\n")
            if "headers" in item:
                f.write("HEADERS:\n")
                for k, v in item["headers"].items():
                    f.write(f"{k}: {v}\n")
            f.write("\nBODY:\n")
            f.write(json.dumps(item.get("body"), ensure_ascii=False, indent=2) if isinstance(item.get("body"), (dict, list)) else str(item.get("body")))
            f.write("\n\n")
            continue
        if "error" in item:
            f.write(json.dumps(item, ensure_ascii=False, indent=2) + "\n")
            continue
        f.write(f"SCENARIO: {item.get('scenario')}\n")
        f.write(f"ID: {item.get('id')}\n")
        f.write(f"URL: {item.get('url')}\n")
        f.write(f"STATUS_CODE: {item.get('status_code')}\n")
        f.write("HEADERS:\n")
        for k, v in (item.get("headers") or {}).items():
            f.write(f"{k}: {v}\n")
        f.write("\nBODY:\n")
        body = item.get("body")
        f.write(json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body, (dict, list)) else str(body))
        f.write("\n\n")

print("Feito")
