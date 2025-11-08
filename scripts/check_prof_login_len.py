# scripts/check_prof_login_len.py
import sqlite3

DBS = [
    r".\pessoas_backup.db",
    r".\instance\pessoas.db",
    r".\app\instance\pessoas.db",
]

for path in DBS:
    try:
        con = sqlite3.connect(path)
        cur = con.cursor()
        row = cur.execute("""
            SELECT id, login, LENGTH(login) AS len_login, perfil, status
            FROM pessoa
            WHERE lower(perfil)='professor'
        """).fetchone()
        con.close()
        print(f"{path} -> {row}")
    except Exception as e:
        print(f"{path} -> ERRO: {e}")
