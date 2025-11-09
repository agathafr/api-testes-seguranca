# tests/seguranca/sql_injection/cenarios/sql_get_pessoa_sqli.py
# Run: python .\tests\seguranca\sql_injection\cenarios\sql_get_pessoa_sqli.py

from pathlib import Path
from datetime import datetime
import shutil
import requests
import json
import urllib.parse
import traceback

URL = "http://127.0.0.1:5000"
BACKUP_DB = Path("pessoas_backup.db")
TARGET_DB = Path("instance") / "pessoas.db"

def restore_db():
    if BACKUP_DB.exists():
        shutil.copyfile(BACKUP_DB, TARGET_DB)

def safe_write(f, text):
    try:
        f.write(text)
    except Exception:
        f.write(f"\n[ERRO DE ESCRITA]: {traceback.format_exc()}\n")

def main():
    restore_db()
    out_folder = Path("respostas") / "sql_injection" / "cenarios" / "sql_get_pessoa_sqli"
    out_folder.mkdir(parents=True, exist_ok=True)
    out_file = out_folder / "sql_get_pessoa_sqli.txt"

    # payloads para testar via path (id)
    payloads = [
        "1",                        # controle
        "1 OR 1=1",                 # versão sem aspas
        "1' OR '1'='1",             # clássico
        "1%20OR%201=1",             # url-encoded espaço
        "0; DROP TABLE pessoa",     # multistatement (provavelmente 404/500)
        "-1",                       # id negativo
        "999999",                   # id alto
        "1' UNION SELECT NULL --",  # tentativa union (pode falhar)
        urllib.parse.quote("' OR '1'='1"),  # encoded variant
    ]

    ses = requests.Session()
    with out_file.open("w", encoding="utf-8") as f:
        safe_write(f, f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
        safe_write(f, "Cenário: GET /pessoas/<id> - tentativa de SQLi via path\n\n")

        for p in payloads:
            try:
                safe_write(f, f"TENTATIVA payload (raw): {p}\n")
                r = ses.get(f"{URL}/pessoas/{p}")
                safe_write(f, f"Rota GET /pessoas/{p} => {r.status_code}\n")
                try:
                    safe_write(f, "RESP (json):\n")
                    safe_write(f, json.dumps(r.json(), ensure_ascii=False, indent=2) + "\n")
                except Exception:
                    safe_write(f, "RESP (texto):\n")
                    safe_write(f, r.text + "\n")
            except requests.RequestException as e:
                safe_write(f, f"RequestException: {repr(e)}\n")
            except Exception:
                safe_write(f, f"Exception: {traceback.format_exc()}\n")

        safe_write(f, "\nFeito. (Verifique códigos 200/401/404/500 e diferenças nas respostas.)\n")

if __name__ == "__main__":
    main()
