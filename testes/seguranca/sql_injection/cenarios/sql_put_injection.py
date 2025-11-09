# tests/seguranca/sql_injection/cenarios/sql_put_injection.py
from pathlib import Path
import shutil
import requests
import json
import time
from datetime import datetime

# --- CONFIGURAÇÕES ---
URL = "http://127.0.0.1:5000"

ALUNO_LOGIN = {"login": "1566256@sga.pucminas.br", "senha": "1566256"}
PROFESSOR_LOGIN = {"login": "377539@sga.pucminas.br", "senha": "377539"}

proprio_aluno_id = 1
outro_id = 2

OUT_FOLDER = Path("respostas") / "sql_injection" / "cenarios" / "sql_put_injection"
OUT_FILE = OUT_FOLDER / "sql_put_injection.txt"
OUT_FOLDER.mkdir(parents=True, exist_ok=True)

PAUSE = 0.25

def safe_write(fobj, text=""):
    try:
        fobj.write(text + "\n")
    except Exception:
        pass

def find_backup_and_dest():
    """
    Procura por 'pessoas_backup.db' subindo a árvore de diretórios a partir do local do script.
    Retorna (backup_path, dest_path) como Path ou (None, None) se não encontrar.
    """
    cur = Path(__file__).resolve().parent
    for p in [cur] + list(cur.parents):
        cand = p / "pessoas_backup.db"
        if cand.exists():
            dest = p / "instance" / "pessoas.db"
            return cand, dest
    return None, None

def restore_db(backup, dest):
    try:
        if backup and dest:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(str(backup), str(dest))
            return True, None
        return False, "backup or dest not found"
    except Exception as e:
        return False, str(e)

def try_login(session, creds):
    try:
        r = session.post(f"{URL}/login", json=creds, timeout=8)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text
    except requests.RequestException as e:
        return None, str(e)

def try_put(session, alvo_id, payload):
    try:
        r = session.put(f"{URL}/pessoas/{alvo_id}", json=payload, timeout=8)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text
    except requests.RequestException as e:
        return None, str(e)

def main():
    BACKUP_DB, DEST_DB = find_backup_and_dest()
    with OUT_FILE.open("w", encoding="utf-8") as f:
        safe_write(f, f"Data de execução: {datetime.utcnow().isoformat()}Z")
        safe_write(f, f"Backup detectado: {BACKUP_DB}")
        safe_write(f, f"DB destino: {DEST_DB}")
        safe_write(f, "")

        scenarios = []

        scenarios.append({
            "login_creds": ALUNO_LOGIN,
            "descricao": "Aluno PUT para elevar/modificar próprio perfil: alterar nome",
            "alvo": proprio_aluno_id,
            "payload": {"nome": "Aluno Injetado - nome alterado pelo próprio"}
        })

        scenarios.append({
            "login_creds": ALUNO_LOGIN,
            "descricao": "Aluno PUT para elevar próprio perfil para 'Professor' (tentativa de elevação)",
            "alvo": proprio_aluno_id,
            "payload": {"perfil": "Professor"}
        })

        scenarios.append({
            "login_creds": ALUNO_LOGIN,
            "descricao": "Aluno PUT tentando alterar perfil de OUTRO usuário",
            "alvo": outro_id,
            "payload": {"perfil": "Professor", "nome": "Tentativa de elevação por outro"}
        })

        scenarios.append({
            "login_creds": PROFESSOR_LOGIN,
            "descricao": "Professor PUT para alterar perfil de OUTRO (controle positivo)",
            "alvo": outro_id,
            "payload": {"perfil": "Aluno", "nome": "Atualizado pelo professor (controle)"}
        })

        sqli_variants = [
            {"perfil": "Professor'; --"},
            {"perfil": "Professor' OR '1'='1"},
            {"nome": "nome_inject', senha='x' --"},
            {"nome": "nome_inject; DROP TABLE pessoa --"},
            {"perfil": "Professor/* */"},
            {"nome": "NormalName", "perfil": "Professor' UNION SELECT 1--"}
        ]
        for idx, p in enumerate(sqli_variants, start=1):
            scenarios.append({
                "login_creds": ALUNO_LOGIN,
                "descricao": f"Tentativa SQLi variante #{idx}",
                "alvo": outro_id,
                "payload": p
            })

        scenarios.append({
            "login_creds": ALUNO_LOGIN,
            "descricao": "Aluno altera propria senha (campo senha) - verificar comportamento",
            "alvo": proprio_aluno_id,
            "payload": {"senha": "novaSenhaTeste123"}
        })

        scenario_index = 0
        for s in scenarios:
            scenario_index += 1
            safe_write(f, f"--- Cenário {scenario_index}: {s['descricao']} ---")
            safe_write(f, f"Credenciais: {s['login_creds']['login']}")
            safe_write(f, f"Alvo (id): {s['alvo']}")
            safe_write(f, f"Payload: {json.dumps(s['payload'], ensure_ascii=False)}")

            # restaura DB antes do cenário (para evitar efeitos colaterais)
            restored, err = restore_db(BACKUP_DB, DEST_DB)
            safe_write(f, f"Restauração antes do cenário: {restored} {('-> ' + err) if err else ''}")
            time.sleep(0.15)

            ses = requests.Session()
            code, body = try_login(ses, s['login_creds'])
            safe_write(f, f"LOGIN status: {code}")
            if isinstance(body, (dict, list)):
                safe_write(f, f"LOGIN body:\n{json.dumps(body, ensure_ascii=False, indent=2)}")
            else:
                safe_write(f, f"LOGIN body: {body}")

            time.sleep(PAUSE)
            put_status, put_body = try_put(ses, s['alvo'], s['payload'])
            safe_write(f, f"PUT /pessoas/{s['alvo']} => {put_status}")
            if isinstance(put_body, (dict, list)):
                safe_write(f, f"RESPONSE JSON:\n{json.dumps(put_body, ensure_ascii=False, indent=2)}")
            else:
                safe_write(f, f"RESPONSE TEXT:\n{str(put_body)}")
            safe_write(f, "")
            time.sleep(PAUSE)

        safe_write(f, "Feito. (Se algum PUT retornou 200 e/ou o conteúdo do banco mudou, evidência de alteração encontrada.)")

if __name__ == "__main__":
    main()
