# testes/seguranca/bfla/cenarios/get_lista_pessoas_sem_login.py
"""
BFLA (SEM autenticação):
Tentar obter a LISTA completa de pessoas via GET /pessoas (sem <id>).

Saída: respostas\bfla\cenarios\get_lista_pessoas_sem_login\get_lista_pessoas_sem_login.txt
"""
import os
import json
import requests
from datetime import datetime

BASE = "http://127.0.0.1:5000"

out_dir = os.path.join("respostas", "bfla", "cenarios", "get_lista_pessoas_sem_login")
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "get_lista_pessoas_sem_login.txt")

def try_get_lista():
    url = f"{BASE.rstrip('/')}/pessoas"
    try:
        r = requests.get(url, timeout=8)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return {
            "ok": True,
            "url": url,
            "status_code": r.status_code,
            "headers": dict(r.headers),
            "body": body
        }
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)}

result = {
    "executed_at": datetime.utcnow().isoformat() + "Z",
    "base": BASE,
    "note": "Sem autenticação deliberadamente (BFLA).",
    "response": try_get_lista()
}

with open(out_file, "w", encoding="utf-8") as f:
    f.write("BFLA – GET /pessoas (lista) sem login\n\n")
    f.write(json.dumps(result, ensure_ascii=False, indent=2))

print("Feito")
