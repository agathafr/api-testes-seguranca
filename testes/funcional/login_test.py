from pathlib import Path
import requests, json

URL = "http://127.0.0.1:5000/login"
payload = {"login": "377539@sga.pucminas.br", "senha": "377539"}
ses = requests.Session()
resp = ses.post(URL, json=payload)

Path("respostas").mkdir(exist_ok=True)
out = Path("respostas/login_normal_py.txt")
with out.open("w", encoding="utf-8") as f:
    f.write(f"STATUS: {resp.status_code}\n\nHEADERS:\n")
    for k,v in resp.headers.items():
        f.write(f"{k}: {v}\n")
    f.write("\nBODY:\n")
    try:
        f.write(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except Exception:
        f.write(resp.text)

# save cookies
with open("cookies_py.txt","w",encoding="utf-8") as f:
    for c in ses.cookies:
        f.write(f"{c.name}={c.value}; domain={c.domain}; path={c.path}\n")

print("Feito. Verifique respostas/login_normal_py.txt e cookies_py.txt")
