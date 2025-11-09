#!/usr/bin/env python3
# sql_error_based.py (improved)
# Aggressive error-based probing, captures exception traces and looks for DB error strings in responses.
# Run: python .\tests\seguranca\sql_injection\cenarios\sql_error_based.py

from pathlib import Path
from datetime import datetime
import shutil, requests, json, traceback, re

BACKUP_DB = Path.cwd() / "pessoas_backup.db"
TARGET_DB = Path.cwd() / "instance" / "pessoas.db"
OUT_DIR = Path("respostas") / "sql_injection" / "cenarios" / "sql_error_based"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / f"sql_error_based_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"

URL = "http://127.0.0.1:5000"
TARGET = "/pessoas/"

PAYLOADS = [
    "1' OR 1=1 -- ",
    "1' UNION SELECT name FROM sqlite_master -- ",
    "1' AND (SELECT 1/0) -- ",
    "1' AND (SELECT cast('a' as integer)) -- ",
    "nonexistent'; SELECT * FROM nao_existe -- ",
    "\" or \"\" = \"",
]

ERROR_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [r"sqlite", r"syntax error", r"traceback", r"exception", r"error"]]

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

def contains_error_indicators(text):
    if not text:
        return False
    for pat in ERROR_PATTERNS:
        if pat.search(text):
            return True
    return False

def main():
    write(f"Data de execução: {datetime.utcnow().isoformat()}Z")
    ok, msg = restore_db()
    write(f"Restore: {ok} - {msg}")
    write(f"Target base: {URL}{TARGET}")
    write("-"*80)
    session = requests.Session()

    for p in PAYLOADS:
        endpoint = f"{URL}{TARGET}{p}"
        write(f"Trying payload (raw): {p}")
        try:
            r = session.get(endpoint, timeout=10)
            write(f"Status: {r.status_code}")
            body = r.text or ""
            try:
                j = r.json()
                write(\"Response JSON:\")
                write(json.dumps(j, ensure_ascii=False, indent=2))
            except Exception:
                write(\"Response text:\")
                write(body[:8000])
            if contains_error_indicators(body):
                write(\"[ALERT] response contains potential DB/error indicators\")
        except Exception as e:
            write(\"[EXCEPTION] \" + str(e))
            write(traceback.format_exc())
        write(\"-\"*60)
    write(\"Resultado final: Feito. (verifique se há erros de DB/tracebacks)\")
    print(\"Done. Evidence:\", OUT_FILE)

if __name__ == '__main__':
    main()
