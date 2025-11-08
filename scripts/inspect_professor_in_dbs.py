# scripts/inspect_professor_in_dbs.py
import os, json, sqlite3, time

ALVO = "377539@gsa.pucminas.br"

DBS = [
    r".\pessoas_backup.db",          # raiz (backup de referência)
    r".\instance\pessoas.db",        # instance na raiz do projeto
    r".\app\instance\pessoas.db",    # instance dentro de app
]

def human_ts(path):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))

def inspeccionar(db_path):
    info = {"db": db_path, "existe": os.path.exists(db_path)}
    if not info["existe"]:
        return info

    info["tamanho_bytes"] = os.path.getsize(db_path)
    info["modificado"] = human_ts(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pessoa'")
        if not cur.fetchone():
            info["erro"] = "Tabela 'pessoa' não existe"
            return info

        cur.execute("SELECT COUNT(*) FROM pessoa")
        info["total_pessoas"] = cur.fetchone()[0]

        cur.execute("SELECT id, login, perfil, status FROM pessoa WHERE lower(perfil)='professor'")
        info["professores"] = cur.fetchall()

        cur.execute("SELECT id, login, perfil, status, senha FROM pessoa WHERE login = ?", (ALVO,))
        rows = cur.fetchall()
        info["alvo"] = [
            (r[0], r[1], r[2], r[3], (r[4][:8] + "…") if r[4] else None) for r in rows
        ]
    finally:
        conn.close()
    return info

resultado = [inspeccionar(p) for p in DBS]
print(json.dumps(resultado, ensure_ascii=False, indent=2))
