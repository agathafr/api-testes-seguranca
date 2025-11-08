from datetime import datetime
import requests

url = "http://127.0.0.1:5000"
login_data = {"login": "377539@sga.pucminas.br", "senha": "377539"}  # Professor

# Login
response = requests.post(f"{url}/login", json=login_data)
cookies = response.cookies
print("Login status:", response.status_code)

# Tentativa de desativar aluno ID 3
target_id = 3
r = requests.post(f"{url}/pessoas/{target_id}/desativar", cookies=cookies)
print("POST /pessoas/3/desativar =>", r.status_code, r.text)

# Salvar evidência
with open("respostas/bfla/cenarios/professor_post_desativar_outro_usuario/professor_post_desativar_outro_usuario.txt", "w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"Login status: {response.status_code}\n")
    f.write(f"POST status: {r.status_code}\n")
    f.write(f"Resposta:\n{r.text}\n")

print("Feito.")
