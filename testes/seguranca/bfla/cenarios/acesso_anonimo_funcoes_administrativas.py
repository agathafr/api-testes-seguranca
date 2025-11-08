import requests
from datetime import datetime
import os

# Configurações
BASE_URL = "http://127.0.0.1:5000"
ROTAS_ADMIN = [
    "/pessoas/1/ativar",
    "/pessoas/1/desativar",
    "/pessoas/1",
]
METODOS = ["GET", "POST", "PUT"]

# Caminho para salvar evidências
cenario = "acesso_anonimo_funcoes_administrativas"
saida_dir = os.path.join("respostas", "bfla", "cenarios", cenario)
os.makedirs(saida_dir, exist_ok=True)
saida_path = os.path.join(saida_dir, f"{cenario}.txt")

# Execução
with open(saida_path, "w", encoding="utf-8") as f:
    f.write(f"=== CENÁRIO: {cenario} ===\n")
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n\n")
    f.write(f"Objetivo: Verificar se endpoints administrativos são acessíveis sem autenticação.\n")
    f.write("=" * 60 + "\n\n")

    for rota in ROTAS_ADMIN:
        for metodo in METODOS:
            url = f"{BASE_URL}{rota}"
            try:
                if metodo == "GET":
                    resp = requests.get(url)
                elif metodo == "POST":
                    resp = requests.post(url)
                elif metodo == "PUT":
                    resp = requests.put(url)
                else:
                    continue

                f.write(f"→ {metodo} {rota}\n")
                f.write(f"Status: {resp.status_code}\n")
                f.write(f"Resposta: {resp.text[:200]}...\n\n")

            except Exception as e:
                f.write(f"Erro ao tentar {metodo} {rota}: {e}\n\n")

    f.write("=" * 60 + "\n")
    f.write("Execução concluída.\n")

print(f"Feito. Saída salva em: {saida_path}")
