# Prática - Testes de Segurança em API Flask

Este projeto contém uma API Flask vulnerável (propósito didático) e um conjunto mínimo de scripts e testes para demonstrar **SQL Injection, BOLA, Elevação de Privilégios e BFLA**. Foi desenvolvido como parte da disciplina **Testes de Segurança**, com o objetivo de demonstrar vulnerabilidades comuns em APIs e a importância da validação de entrada, autenticação e autorização adequadas.

> **Quick start:** veja o guia prático — [README-dev.md](README-dev.md) ← clique aqui para os comandos copy-paste

---

## 1. Visão geral

A aplicação é uma **API Flask** simples, desenvolvida intencionalmente com falhas de segurança para permitir a execução e observação de testes automatizados.

As vulnerabilidades abordadas incluem:
- **SQL Injection**
- **BOLA (Broken Object Level Authorization)**
- **Elevação de Privilégio**
- **BFLA (Broken Function Level Authorization)**

Cada vulnerabilidade possui seus testes automatizados, localizados em `testes/seguranca/`, e suas evidências correspondentes em `relatorio/evidencias/<vulnerabilidade>/`.

---

## 2. Estrutura do projeto

```
app/
 ├── __init__.py
 ├── routes.py
 ├── models.py
 ├── database.py
 └── instance/pessoas.db

scripts/
 ├── create_db.py
 ├── import_csv.py
 ├── fix_senhas_plain.py

testes/
 ├── funcional/
 │   └── login_test.py
 └── seguranca/
     ├── sql_injection_test.py
     ├── bola_test.py
     └── (demais testes futuros)

respostas/
 ├── login/
 ├── sql_injection/
 ├── bola/
 └── cookies/

relatorio/
 └── evidencias/
     ├── sql_injection/
     ├── bola/
     └── (demais vulnerabilidades)

README.md
README-dev.md
README-professor.md
requirements.txt
.gitignore
```

---

## 3. Execução rápida

Para execução detalhada, consulte o guia [`README-dev.md`](README-dev.md).  
Abaixo está um resumo simplificado do fluxo:

```powershell
# 1. Criar ambiente virtual e instalar dependências
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r app\requirements.txt

# 2. Iniciar API (em um terminal)
python .\app\routes.py

# 3. Executar testes (em outro terminal com venv ativo)
python .\testes\funcional\login_test.py
python .\testes\seguranca\sql_injection_test.py
python .\testes\seguranca\bola_test.py
```

---

## 4. Evidências

As evidências geradas pelos testes (arquivos `.txt` e imagens `.png`) estão organizadas em:

```
relatorio/
 └── evidencias/
     ├── sql_injection/
     │   ├── resumo_sqli.txt
     │   ├── sqli_or_true.txt
     │   └── sqli_or_true_terminal.png
     ├── bola/
     │   ├── login_aluno.txt
     │   ├── get_pessoa_19_com_sessao_aluno.txt
     │   └── bola_terminal.png
     └── (demais vulnerabilidades)
```

Cada pasta contém:
- O **request/response bruto** (`.txt`)
- O **resumo** (linhas-chave: `STATUS_CODE`, `Set-Cookie`, etc.)
- O **print do terminal** (arquivo `.png`)

---

## 5. Testes de segurança implementados

### 🔹 SQL Injection
- **Objetivo:** verificar se a API é vulnerável a injeções SQL simples.  
- **Local:** `testes/seguranca/sql_injection_test.py`
- **Evidências:** `relatorio/evidencias/sql_injection/`
- **Resultado esperado:** a API **não deve** retornar dados válidos ao receber payloads como `' OR '1'='1`.

### 🔹 BOLA (Broken Object Level Authorization)
- **Objetivo:** verificar se um usuário autenticado pode acessar dados de outro usuário.  
- **Local:** `testes/seguranca/bola_test.py`
- **Evidências:** `relatorio/evidencias/bola/`
- **Resultado esperado:** a API **deve bloquear** o acesso a registros pertencentes a outros usuários.

### 🔹 Elevação de Privilégio e BFLA (em desenvolvimento)
- **Objetivo:** demonstrar exploração de endpoints restritos por função.
- **Status:** implementação futura.

---

## 6. Boas práticas adotadas

- Organização clara de **testes funcionais** e **de segurança**
- Separação entre **saídas brutas (`respostas/`)** e **evidências finais (`relatorio/evidencias/`)**
- Scripts auxiliares (`scripts/`) para manipulação do banco e automação
- README dividido entre:
  - `README.md` → documentação geral
  - `README-dev.md` → instruções práticas (execução passo-a-passo)
  - `README-professor.md` → instruções originais

---

## 7. Requisitos de ambiente

- Python 3.10+
- PowerShell ou terminal compatível
- Pacotes listados em `app/requirements.txt`

---

## 8. Conclusão

Este projeto demonstra, de forma prática, como vulnerabilidades de segurança podem ser detectadas e documentadas em aplicações Flask.  
As evidências e scripts de teste permitem reproduzir e compreender falhas clássicas como **SQL Injection** e **BOLA** de forma controlada e didática.

---

© 2025 — Projeto desenvolvido para fins educacionais.




