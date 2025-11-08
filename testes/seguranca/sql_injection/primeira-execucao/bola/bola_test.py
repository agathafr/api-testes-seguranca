# testes/seguranca/bola_test.py
from pathlib import Path
import requests, json, time

BASE = "http://127.0.0.1:5000"
OUT_DIR = Path("respostas/bola")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# credenciais de um usuário comum (aluno) que existe no DB
payload_login = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}

# id alvo — tentei escolher um id diferente (ajuste se necessário)
alvo_id = 19  # id de outro usuário (professor) — objetivo: provar acesso indevido

def save(name: str, resp):
    p = OUT_DIR / f"{name}.txt"
    with p.open("w", encoding="utf-8") as f:
        f.write("REQUEST JSON:\n")
        try:
            f.write(json.dumps(resp.request.body.decode() if hasattr(resp.request, 'body') and resp.request.body else {}, ensure_ascii=False) + "\n\n")
        except Exception:
            f.write(str(resp.request.body) + "\n\n")
        f.write("STATUS_CODE:\n")
        f.write(str(resp.status_code) + "\n\n")
        f.write("HEADERS:\n")
        for k, v in resp.headers.items():
            f.write(f"{k}: {v}\n")
        f.write("\nBODY:\n")
        try:
            f.write(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception:
            f.write(resp.text)

def main():
    ses = requests.Session()
    # 1) login
    resp_login = ses.post(f"{BASE}/login", json=payload_login, timeout=10)
    save("login_aluno", resp_login)
    time.sleep(0.2)

    # 2) tenta acessar dados de outro usuário
    resp_get = ses.get(f"{BASE}/pessoas/{alvo_id}", timeout=10)
    save(f"get_pessoa_{alvo_id}_com_sessao_aluno", resp_get)
    print("[OK] salvos em respostas/bola")

if __name__ == "__main__":
    main()
