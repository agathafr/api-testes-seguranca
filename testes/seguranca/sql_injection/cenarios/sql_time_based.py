#!/usr/bin/env python3
# sql_time_based.py (improved)
# Time-based heuristic for SQLite: uses randomblob of increasing size and multiple samples per payload to reduce noise.
# Run: python .\tests\seguranca\sql_injection\cenarios\sql_time_based.py

from pathlib import Path
from datetime import datetime
import shutil, requests, time, json, traceback, os, statistics, urllib.parse

BACKUP_DB = Path.cwd() / "pessoas_backup.db"
TARGET_DB = Path.cwd() / "instance" / "pessoas.db"
OUT_DIR = Path("respostas") / "sql_injection" / "cenarios" / "sql_time_based"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / f"sql_time_based_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"

APP_BASE = "http://127.0.0.1:5000"
TARGET_PATH = "/pessoas/1"

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

def measure(session, inj, samples=5):
    url = APP_BASE + TARGET_PATH + "+" + urllib.parse.quote_plus(inj)
    timings = []
    statuses = []
    for i in range(samples):
        start = time.time()
        try:
            r = session.get(url, timeout=30)
            elapsed = time.time() - start
            timings.append(elapsed)
            statuses.append(r.status_code)
            time.sleep(0.12)
        except Exception as e:
            timings.append(None)
            statuses.append(None)
    vals = [t for t in timings if t is not None]
    stats = {"samples": samples, "mean": statistics.mean(vals) if vals else None, "stdev": statistics.stdev(vals) if len(vals)>1 else None}
    return {"timings": timings, "statuses": statuses, "stats": stats}

def main():
    write(f"Data de execução: {datetime.utcnow().isoformat()}Z")
    ok, msg = restore_db()
    write(f"Restore: {ok} - {msg}")
    write(f"Target: {APP_BASE}{TARGET_PATH}")
    write("-"*80)
    session = requests.Session()

    # Heuristic payloads: increasingly heavy randomblob hex expressions (SQLite)
    # Tune sizes to your machine; if too slow, reduce sizes.
    sizes = [100000, 300000, 700000]  # bytes for randomblob
    payloads = []
    for sz in sizes:
        expr = f"1' AND (SELECT hex(randomblob({sz}))) LIKE '%' --"
        payloads.append((f"rb_{sz}", expr))

    payloads.insert(0, ("control", "1"))

    for name, inj in payloads:
        write(f"Payload: {name}")
        res = measure(session, inj, samples=4)
        write(json.dumps({"payload": name, "inj": inj, "res": res}, ensure_ascii=False, indent=2))
        write("---")
        time.sleep(0.25)

    write("Resultado final: Feito. Interprete médias e desvios para identificar delays significativos.")
    print("Done. Evidence:", OUT_FILE)

if __name__ == '__main__':
    main()
