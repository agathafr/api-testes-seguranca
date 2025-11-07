# testes/seguranca/elevacao_privilegios_test.py
from pathlib import Path
import requests, json, time, os

BASE = "http://127.0.0.1:5000"
OUT_DIR = Path("respostas/bola")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "ativar_sem_permissao.txt"

# Credenciais de aluno (do CSV)
LOGIN = "1566256@sga.pucminas.br"
SENHA = "1566256"

def save_response(path: Path, resp: requests.Response, session: requests.Session):
    with path.open("w", encoding="utf-8") as f:
        f.write(f"REQUEST URL: {resp.request.method} {resp.request.url}\n")
        f.write(f"STATUS: {resp.status_code}\n\n")
        f.write("REQUEST HEADERS:\n")
        for k, v in resp.request.headers.items():
            f.write(f"{k}: {v}\n")
        f.write("\nRESPONSE HEADERS:\n")
        for k, v in resp.headers.items():
            f.write(f"{k}: {v}\n")
        f.write("\nCOOKIES:\n")
        if session.cookies:
            for k, v in session.cookies.get_dict().items():
                f.write(f"{k}={v}\n")
        else:
            f.write("(sem cookies)\n")
        f.write("\nBODY:\n")
        try:
            f.write(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception:
            f.write(resp.text)

def main():
    s = requests.Session()
    # 1) login como Aluno
    login_url = f"{BASE}/login"
    resp_login = s.post(login_url, json={"login": LOGIN, "senha": SENHA})
    # tenta descobrir ID do usuário logado (se retornado no body)
    try:
        body = resp_login.json()
    except Exception:
        body = {}
    my_id = None
    if isinstance(body, dict) and "id" in body:
        my_id = body.get("id")
    # 2) tenta obter lista de pessoas para escolher alvo diferente
    target_id = None
    try:
        resp_list = s.get(f"{BASE}/pessoas")
        try:
            people = resp_list.json()
            # espera que seja lista de objetos com 'id' e 'login'
            if isinstance(people, list) and len(people) > 0:
                for p in people:
                    pid = p.get("id")
                    if pid is None:
                        continue
                    if my_id is None or pid != my_id:
                        target_id = pid
                        break
        except Exception:
            pass
    except Exception:
        pass

    # Se não conseguiu descobrir, tenta id 2 por padrão
    if target_id is None:
        target_id = 2
        if my_id == 2:
            target_id = 3

    # 3) tenta ativar/desativar a pessoa alvo como Aluno (sem permissão esperada)
    ativar_url = f"{BASE}/pessoas/{target_id}/ativar"
    try:
        resp_ativar = s.post(ativar_url)
    except Exception as e:
        # salva erro
        with OUT_FILE.open("w", encoding="utf-8") as f:
            f.write("ERRO AO REALIZAR REQUEST:\n")
            f.write(str(e))
        print("Feito")
        return

    # salvar evidência
    save_response(OUT_FILE, resp_ativar, s)
    print("Feito")

if __name__ == "__main__":
    main()
