# PRATICA-TESTES-SEGURANCA — README-dev (instruções rápidas)

Este README contém os comandos/fluxo rápido para executar a aplicação localmente, preparar o banco e gerar as evidências usadas na prática.

> Observação: existe também o `README-professor.md`. Este `README-dev.md` complementa-o com passos práticos e específicos do ambiente Windows/PowerShell.

---

## 1) Criar e ativar ambiente virtual (Windows / PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2) Instalar dependências
```powershell
pip install -r app\requirements.txt
```

## 3) Preparar o banco de dados (apenas se necessário)
Os scripts estão em `scripts/`. Execute na ordem (em um terminal com venv ativado):

```powershell
python .\scripts\create_db.py         # cria o schema inicial (se aplicável)
python .\scripts\import_csv.py        # popula a tabela com listagem.csv
python .\scripts\fix_senhas_plain.py  # normaliza/ajusta senhas em texto puro
```

> Se já houver `app\instance\pessoas.db` com dados, pule a etapa de import.

## 4) Iniciar a API (manter este terminal aberto)
```powershell
python .\app\routes.py
# A API irá rodar em http://127.0.0.1:5000
```

## 5) Abrir novo terminal (com venv ativado) e rodar os testes
```powershell
.env\Scripts\Activate.ps1
# Teste funcional (ex.: login)
python .\testes\funcional\login_test.py

# Testes de segurança
python .\testes\seguranca\sql_injection_test.py
python .\testes\seguranca\bola_test.py
```

## 6) Onde ficam as saídas / evidências (importante)
- **Respostas brutas** geradas pelos scripts de teste ficam em:
  - `respostas\login\` (logs/req-resp do login)
  - `respostas\sql_injection\` (outputs dos payloads)
  - `respostas\bola\`, `respostas\cookies\` etc.

- **Evidências finais (para o relatório)**: copie / mova os arquivos relevantes para:
  - `relatorio\evidencias\<categoria>\`  
    exemplos:
    - `relatorio\evidencias\sql_injection\`
    - `relatorio\evidencias\bola\`
    - `relatorio\evidencias\cookies\`

  Essa separação facilita montar o PDF de entrega (um lugar apenas com as evidências selecionadas).

## 7) Captura de telas do terminal
- Salve as imagens (screenshots) **em PNG** dentro da pasta de evidências correspondente:
  - Ex.: `relatorio\evidencias\sql_injection\sql_or_true_terminal.png`
  - Ex.: `relatorio\evidencias\bola\bola_terminal.png`
- Nomeie de forma descritiva (ex.: `sql_or_true_terminal.png`, `get_pessoa_19_com_sessao_aluno.txt`) para facilitar o relatório.

## 8) Resumo automático das evidências (comandos úteis)
- Ver as primeiras linhas da resposta de login:
```powershell
Get-Content .\respostas\login\login_normal_py.txt -TotalCount 20
```
- Ver saída de um payload de SQLi:
```powershell
Get-Content .\respostas\sql_injection\sqli_or_true.txt -TotalCount 20
```
- Consolidar resultados em `relatorio\evidencias\...`:
```powershell
# exemplo: copiar respostas geradas para relatório/evidencias
Copy-Item .\respostas\sql_injection\* -Destination .\relatorio\evidencias\sql_injection\ -Force
```

## 9) .gitignore recomendado (sugestão)
Adicione/atualize `.gitignore` na raiz assim:
```
venv/
*.db
respostas/
relatorio/evidencias/
*.pyc
__pycache__/
.env
```
> Observação: mantemos `relatorio/evidencias/` fora do repositório por conterem evidências; se quiser versionar evidências, remova-as do gitignore.

---

## Boas práticas e organização do projeto
- **Scripts** (ferramentas de manipulação) → `scripts/` (já criado)
- **Testes** → `testes/funcional` e `testes/seguranca`
- **Respostas brutas** (outputs automáticos) → `respostas/<categoria>/`
- **Evidências finais para o relatório** → `relatorio/evidencias/<categoria>/` (apenas os arquivos mais relevantes)
- **README-professor.md** permanece na raiz.
- **README.md**: arquivo principal com a descrição teórica; `README-dev.md` é o guia rápido de execução.

---

## Próximo passo sugerido (fluxo passo-a-passo)
Eu vou seguir o método passo-a-passo que você pediu: quando confirmar que quer seguir, darei uma única instrução por vez e esperarei você executar e me enviar o retorno.

**Depois de salvar este README-dev.md**, diga **"pronto"** e eu envio a 1ª instrução (por exemplo: "1) Ative o venv e me diga o resultado de `python --version`"), e assim seguiremos até completar a prática.

---

> Voltar à documentação completa: [README.md](README.md)
