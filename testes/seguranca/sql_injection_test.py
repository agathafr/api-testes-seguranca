# testes/seguranca/sql_injection_test.py
from pathlib import Path
import requests, json, re, time

BASE = "http://127.0.0.1:5000"
OUT_DIR = Path("respostas/sql_injection")
OUT_DIR.mkdir(parents=True, exist_ok=True)

payloads = [
    {"name":"sqli_or_true", "login": "1566256@sga.pucminas.br' OR '1'='1", "senha":"x"},
    {"name":"sqli_or_true_dash", "login": "1566256@sga.pucminas.br' OR '1'='1' -- ", "senha":"x"},
    {"name":"sqli_tautology", "login": "' OR '1'='1", "senha":"anything"},
]

def safe_fname(s: str) -> str:
    return re.sub(r'[^0-9A-Za-z_.-]', '_', s)[:60]

for p in payloads:
    name = p["name"]
    payload = {"login": p["login"], "senha": p["senha"]}
    try:
        ses = requests.Session()
        resp = ses.post(f"{BASE}/login", json=payload, timeout=10)
        out_path = OUT_DIR / f"{safe_fname(name)}.txt"
        with out_path.open("w", encoding="utf-8") as f:
            f.write("REQUEST JSON:\n")
            f.write(json.dumps(payload, ensure_ascii=False) + "\n\n")
            f.write("STATUS_CODE:\n")
            f.write(str(resp.status_code) + "\n\n")
            f.write("HEADERS:\n")
            for k,v in resp.headers.items():
                f.write(f"{k}: {v}\n")
            f.write("\nBODY:\n")
            try:
                f.write(json.dumps(resp.json(), ensure_ascii=False, indent=2))
            except Exception:
                f.write(resp.text)
        print(f"[OK] saved {out_path}")
        # small pause so you can observe server logs if open
        time.sleep(0.3)
    except Exception as e:
        err_path = OUT_DIR / f"{safe_fname(name)}_error.txt"
        with err_path.open("w", encoding="utf-8") as f:
            f.write(str(e))
        print(f"[ERR] saved {err_path}")
