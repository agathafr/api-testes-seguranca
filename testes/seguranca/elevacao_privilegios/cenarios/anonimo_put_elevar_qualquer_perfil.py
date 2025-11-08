# testes/seguranca/elevacao_privilegios/cenarios/anonimo_put_elevar_qualquer_perfil.py
from datetime import datetime
from pathlib import Path
import requests
import json

URL = "http://127.0.0.1:5000"
alvo_id = 2                     # qualquer usuário existente (ex.: Aluno B)
novo_perfil = "professor"       # tentativa de elevação sem login

# pasta de saída (respostas)
out = Path("respostas/elevacao_privilegios/cenarios/anonimo_put_elevar_qualquer_perfil/anonimo_put_elevar_qualquer_perfil.txt")
out.parent.mkdir(parents=True, exist_ok=True)

with out.open("w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"Tentativa: PUT /pessoas/{{id}} sem login (elevar para '{novo_perfil}')\n")

    payload = {"perfil": novo_perfil}
    r = requests.put(f"{URL}/pessoas/{alvo_id}", json=payload)

    f.write(f"\nPUT /pessoas/{alvo_id} => {r.status_code}\n")
    try:
        f.write("RESPOSTA (json):\n" + json.dumps(r.json(), ensure_ascii=False, indent=2) + "\n")
    except Exception:
        f.write("RESPOSTA (texto):\n" + r.text + "\n")

print("Feito. (Sem login deve retornar 401; se vier 200/403 com troca de perfil, há falha.)")
