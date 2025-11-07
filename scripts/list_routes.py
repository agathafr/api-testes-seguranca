# scripts/list_routes.py
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent      # raiz do projeto
APP_DIR = ROOT / "app"                             # pasta onde está routes.py

# garante que a pasta 'app' está no PYTHONPATH
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
    
import routes

print("=== URL MAP (raw) ===")
print(routes.app.url_map)

print("\n=== Rotas detalhadas ===")
for rule in routes.app.url_map.iter_rules():
    methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
    print(f"{rule.rule:30}  ->  endpoint: {rule.endpoint:20}  methods: {methods}")
