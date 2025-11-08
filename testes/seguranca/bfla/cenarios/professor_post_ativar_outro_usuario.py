from datetime import datetime
import requests

url = "http://127.0.0.1:5000"
login_data = {"login": "377539@sga.pucminas.br", "senha": "377539"}  # Professor

# Login
response = requests.post(f"{url}/login", json=login_data)
cookies = response.cookies
print("Login status:", response.status_code)

# Tentativa de ativar aluno ID 2
target_id = 2
r = requests.post(f"{url}/pessoas/{target_id}/ativar", cookies=cookies)
print("POST /pessoas/2/ativar =>", r.status_code, r.text)

# Salvar evidência
with open("respostas/bfla/cenarios/professor_post_ativar_outro_usuario/professor_post_ativar_outro_usuario.txt", "w", encoding="utf-8") as f:
    f.write(f"Data de execução: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"Login status: {response.status_code}\n")
    f.write(f"POST status: {r.status_code}\n")
    f.write(f"Resposta:\n{r.text}\n")

print("Feito.")
