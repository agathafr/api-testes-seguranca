# tests/seguranca/sql_injection/cenarios/sql_login_bypass_auth_fixed.py
"""
Script de teste: sql_login_bypass_auth_fixed.py
- Restaura o DB a partir de pessoas_backup.db (cópia para instance/pessoas.db)
- Testa payloads clássicos de login bypass (POST /login)
- Para cada payload: envia 3 variantes (raw, escapado para SQL, urlencoded)
- Registra tudo em respostas/sql_injection/cenarios/sql_login_bypass_auth/sql_login_bypass_auth.txt
- Continua em caso de erro (não interrompe). 
"""
from datetime import datetime
from pathlib import Path
import shutil
import requests
import json
import urllib.parse
import time
import traceback

URL = "http://127.0.0.1:5000"
BACKUP_DB = Path("pessoas_backup.db")
TARGET_DB = Path("instance") / "pessoas.db"

OUT_FOLDER = Path("respostas") / "sql_injection" / "cenarios" / "sql_login_bypass_auth"
OUT_FOLDER.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_FOLDER / "sql_login_bypass_auth.txt"

# payloads clássicos (bypass). Ajuste se quiser adicionar/remover.
PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' -- ",
    "' OR 1=1 -- ",
    "\" OR \"1\"=\"1",
    "1' OR '1'='1",
    "' OR 'x'='x",
    "' OR ''='",        # tentativa estranha, pode causar erros mas vamos registrar
    "admin' OR '1'='1",
    "\" OR 1=1 -- ",
]

SLEEP_BETWEEN = 0.12  # pequeno delay para não spammar

def restore_db():
    try:
        if not BACKUP_DB.exists():
            return f"Backup não encontrado em {BACKUP_DB.resolve()}"
        TARGET_DB.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BACKUP_DB, TARGET_DB)
        return f"Banco restaurado: {BACKUP_DB} -> {TARGET_DB}"
    except Exception as e:
        return f"Falha ao restaurar DB: {e}"

def write_line(text: str):
    with OUT_FILE.open("a", encoding="utf-8") as f:
        f.write(text + "\n")

def try_post(payload_login, payload_senha, session: requests.Session):
    """
    Envia POST /login com json {"login":..., "senha":...}
    Retorna dicionário com resultado (status, body, error)
    """
    result = {"status": None, "body": None, "error": None}
    try:
        r = session.post(f"{URL}/login", json={"login": payload_login, "senha": payload_senha}, timeout=8)
        result["status"] = r.status_code
        try:
            result["body"] = r.json()
        except Exception:
            result["body"] = r.text[:4000]
    except requests.RequestException as e:
        result["error"] = f"RequestException: {repr(e)}"
    except Exception as e:
        result["error"] = f"Exception: {repr(e)}\n{traceback.format_exc()}"
    return result

def variants_of(p: str):
    """Gera variantes: raw, SQL-escaped (''), urlencoded"""
    raw = p
    escaped = p.replace("'", "''")  # dupla-aspas simples para literais SQL (pode neutralizar injection)
    urlencoded = urllib.parse.quote_plus(p)
    return [("raw", raw), ("escaped", escaped), ("urlencoded", urlencoded)]

def main():
    # limpa arquivo anterior
    if OUT_FILE.exists():
        OUT_FILE.unlink()
    write_line(f"Data de execução: {datetime.utcnow().isoformat()}Z")
    write_line(restore_db())
    write_line("")
    write_line("Cenário: POST /login com payloads de SQLi (bypass) - versão robusta")
    write_line("Observações: para evidência, registramos status 200/401/403/404/500. O script segue mesmo diante de erros.")
    write_line("----\n")

    session = requests.Session()
    results = []

    for where in ("login", "senha"):
        for p in PAYLOADS:
            for tag, variant in variants_of(p):
                # Prepare payloads; test only altering the 'where' field, keep the other field benign
                if where == "login":
                    pl_login = variant
                    pl_senha = "1566256"  # senha válida conhecida (padrão)
                else:
                    pl_login = "1566256@sga.pucminas.br"  # login válido conhecido
                    pl_senha = variant

                entry = {
                    "when": datetime.utcnow().isoformat() + "Z",
                    "campo": where,
                    "payload_original": p,
                    "variant_tag": tag,
                    "variant_value": variant,
                    "status": None,
                    "body": None,
                    "error": None,
                }

                res = try_post(pl_login, pl_senha, session)
                entry["status"] = res.get("status")
                entry["body"] = res.get("body")
                entry["error"] = res.get("error")

                # registro em arquivo
                write_line("----")
                write_line(f"when: {entry['when']}")
                write_line(f"campo: {entry['campo']}")
                write_line(f"payload_original: {entry['payload_original']!r}")
                write_line(f"variant: {entry['variant_tag']}")
                write_line(f"variant_value: {entry['variant_value']!r}")
                write_line(f"status: {entry['status']}")
                write_line("body:")
                try:
                    if isinstance(entry["body"], (dict, list)):
                        write_line(json.dumps(entry["body"], ensure_ascii=False, indent=2))
                    else:
                        write_line(str(entry["body"]))
                except Exception:
                    write_line(f"<falha ao serializar body: {repr(entry['body'])}>")
                if entry["error"]:
                    write_line("error:")
                    write_line(str(entry["error"]))
                write_line("")

                results.append(entry)
                time.sleep(SLEEP_BETWEEN)

    # resumo simples
    succ = [r for r in results if r["status"] == 200]
    write_line("==== RESUMO ====")
    write_line(f"Total de tentativas: {len(results)}")
    write_line(f"Total 200 detectados: {len(succ)}")
    if succ:
        write_line("Detalhe 200s:")
        for s in succ:
            write_line(f" - when {s['when']} campo {s['campo']} payload {s['payload_original']!r} variant {s['variant_tag']} value {s['variant_value']!r}")
    else:
        write_line("Nenhum 200 detectado.")

    print("Feito. Arquivo:", OUT_FILE)

if __name__ == "__main__":
    main()
