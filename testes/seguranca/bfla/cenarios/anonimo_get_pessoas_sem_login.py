# testes/seguranca/bfla/cenarios/get_pessoas_sem_login.py
"""
BFLA dirigido (SEM autenticação):
Tentar ler dados sensíveis via GET /pessoas/<id> sem sessão.

Saída: respostas\bfla\cenarios\get_pessoas_sem_login\get_pessoas_sem_login.txt
"""
import os
import json
import requests
from datetime import datetime

BASE = "http://127.0.0.1:5000"
TARGET_IDS = [1, 2, 3, 19]  # ajuste se quiser

out_dir = os.path.join("respostas", "bfla", "cenarios", "get_pessoas_sem_login")
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "get_pessoas_sem_login.txt")

def fetch(id_):
    url = f"{BASE.rstrip('/')}/pessoas/{id_}"
    try:
        r = requests.get(url, timeout=8)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return {
            "id": id_,
            "url": url,
            "status_code": r.status_code,
            "headers": dict(r.headers),
            "body": body
        }
    except Exception as e:
        return {"id": id_, "url": url, "error": str(e)}

results = []
results.append({"meta": {
    "executed_at": datetime.utcnow().isoformat() + "Z",
    "base": BASE,
    "note": "Sem autenticação deliberadamente (BFLA)."
}})

for tid in TARGET_IDS:
    results.append(fetch(tid))

with open(out_file, "w", encoding="utf-8") as f:
    f.write("BFLA – GET /pessoas/<id> sem login\n\n")
    for item in results:
        if "meta" in item:
            f.write(json.dumps(item["meta"], ensure_ascii=False, indent=2) + "\n\n")
            continue
        f.write("----\n")
        f.write(f"ID: {item.get('id')}\n")
        f.write(f"URL: {item.get('url')}\n")
        if "error" in item:
            f.write(f"ERROR: {item['error']}\n\n")
            continue
        f.write(f"STATUS_CODE: {item.get('status_code')}\n")
        f.write("HEADERS:\n")
        for k, v in (item.get("headers") or {}).items():
            f.write(f"{k}: {v}\n")
        f.write("\nBODY:\n")
        try:
            f.write(json.dumps(item.get("body"), ensure_ascii=False, indent=2))
        except Exception:
            f.write(str(item.get("body")))
        f.write("\n\n")

print("Feito")
