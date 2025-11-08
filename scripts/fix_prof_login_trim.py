# scripts/fix_prof_login_trim.py
import sqlite3

DBS = [
    r".\pessoas_backup.db",
    r".\instance\pessoas.db",
    r".\app\instance\pessoas.db",
]

for path in DBS:
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("""
        UPDATE pessoa
        SET login = TRIM(login)
        WHERE lower(perfil) = 'professor'
    """)
    con.commit()
    updated = cur.rowcount
    con.close()
    print(f"{path}: login do professor ajustado ({updated} registro atualizado).")
