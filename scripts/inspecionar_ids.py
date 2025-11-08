# scripts/inspecionar_ids.py
import sqlite3
from pathlib import Path
import argparse
import csv

# Possíveis bancos do seu projeto
CANDIDATOS = [
    Path("pessoas_backup.db"),
    Path("instance/pessoas.db"),
    Path("app/instance/pessoas.db"),
]

def achar_db():
    for p in CANDIDATOS:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError("Nenhum pessoas.db encontrado nos caminhos padrão.")

def obter_colunas(cur):
    cur.execute("PRAGMA table_info(pessoa)")
    cols = [r[1] for r in cur.fetchall()]  # r[1] = nome da coluna
    # Só vamos selecionar as colunas que realmente existem
    desejadas = [c for c in ("id", "nome", "login", "perfil", "status") if c in cols]
    if not desejadas:
        raise RuntimeError("Não encontrei colunas esperadas na tabela 'pessoa'.")
    return desejadas

def dump_pessoas(db_path: Path, filtro_login: str | None):
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    cols = obter_colunas(cur)
    cur.execute(f"SELECT {', '.join(cols)} FROM pessoa ORDER BY id")
    linhas = cur.fetchall()

    print(f"\nBanco: {db_path}")
    print(f"Colunas: {cols}\n")
    for row in linhas:
        registro = dict(zip(cols, row))
        print(registro)

    if filtro_login and "login" in cols:
        print(f"\nFiltro --login: {filtro_login}")
        achados = [dict(zip(cols, r)) for r in linhas if r[cols.index("login")] == filtro_login]
        if achados:
            for r in achados:
                print(r)
        else:
            print("Não encontrado.")

    # Salva evidência em CSV
    outdir = Path("respostas/bola")
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "dump_ids_pessoas.csv"
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(linhas)
    print(f"\nEvidência salva: {outfile}")

    con.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Inspeciona IDs e logins na tabela pessoa.")
    ap.add_argument("--login", help="Opcional: filtra um login específico (ex.: 1566256@sga.pucminas.br)")
    args = ap.parse_args()

    db = achar_db()
    dump_pessoas(db, args.login)
