# testes/seguranca/bola/cenarios/anonimo_get_pessoa_por_id.py
from datetime import datetime
import requests
from pathlib import Path
import json

URL = "http://127.0.0.1:5000"
alvo_id = 2

Path("respostas/bola/cenarios/anonimo_get_pessoa_por_id").mkdir(parents=True, exist_ok=True)
out = Path("respostas/bola/cenarios/anonimo_get_pessoa_por_id/anonimo_get_pessoa_por_id.txt")

r = requests.get(f"{URL}/pessoas/{alvo_id}", headers={"Accept": "application/json"}, timeout=10)

with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"GET /pessoas/{alvo_id} (sem login) => {r.status_code}\n")
    try:
        f.write(f"RESPOSTA:\n{json.dumps(r.json(), ensure_ascii=False, indent=2)}\n")
    except Exception:
        f.write(f"RESPOSTA (texto):\n{r.text}\n")

    # 🔍 Interpretação automática
    msg = "Proteção aplicada (401 esperado)." if r.status_code == 401 else "⚠️ Possível exposição (esperado 401)."
    f.write(f"\nINTERPRETAÇÃO: {msg}\n")

print(msg)
print("Feito. (Esperado 401.)")
