# Plano de Testes de Segurança — Prática

**Projeto:** PRATICA-TESTES-SEGURANCA  
**Data:** 2025-11-07  
**Objetivo:** definir casos de teste passo a passo para identificar e documentar as vulnerabilidades listadas na prática: **SQL Injection**, **Broken Object Level Authorization (BOLA)**, **Elevação de Privilégios**, e **Broken Function Level Authorization (BFLA)**.

---

## Instruções gerais (como executar e coletar evidências)
1. Execute a API localmente: `python .\app\routes.py` (siga o README-dev para ativar venv e preparar DB).  
2. Para cada caso de teste: execute somente o passo atual. Só avance para o próximo quando o caso atual estiver concluído e evidências salvas.  
3. Evidências a salvar:  
   - Saída do terminal (screenshot) mostrando request/resposta e status code. Nome sugerido: `nomecaso_terminal.png`.  
   - Arquivo de resposta salvo (já há script de testes que grava respostas em `respostas/<categoria>/`. Ex.: `respostas/sql_injection/sqli_or_true.txt`)  
   - Arquivo resumo dentro `relatorio/evidencias/<categoria>/resumo_<categoria>.txt` contendo: objetivo, passos executados, payloads usados, resultado e conclusão.  
4. Estrutura sugerida de evidências (já usada no projeto):  
   - `relatorio/evidencias/sql_injection/`  
   - `relatorio/evidencias/bola/`  
   - `relatorio/evidencias/privilege_escalation/`  
   - `relatorio/evidencias/login/` (para evidências de autenticação)  
   - Use nomes de arquivos claros, por exemplo: `sql_injection_terminal.png`, `sqli_or_true.txt`, `resumo_sqli.txt`.  
5. Anote data/hora e comando exato usado em cada evidência (útil para relatório).

---

## Mapa rápido de endpoints (verifique com `python .\scripts\list_routes.py` se disponível)
Exemplos possíveis (ajuste conforme as rotas reais):  
- `POST /login` — autenticação (retorna cookie de sessão).  
- `GET /pessoas/<id>` — obter dados de pessoa.  
- `PUT /pessoas/<id>` — atualizar dados de pessoa.  
- `POST /pessoas` — criar pessoa (se existir).

> Ajuste ids e URLs de acordo com `routes.py` e com a sua DB (`instance/pessoas.db`).

---

## Planilha de Casos de Teste (passo a passo)

### Caso 1 — SQL Injection (teste básico: `' OR '1'='1`)
- **Objetivo:** verificar se endpoint de login ou consulta aceita injeção que retorna sucesso indevido.  
- **Pré-condição:** servidor rodando; DB com pelo menos 1 usuário (`id=1`).  
- **Endpoint alvo:** `POST /login` (ou outro endpoint que use login).  
- **Payloads (exemplos):**  
  1. `{"login": "1566256@sga.pucminas.br' OR '1'='1", "senha": "x"}`  
  2. `{"login": "any' OR '1'='1' -- ", "senha": "anything"}`  
  3. tautology com `--` ou `;` se aplicável.  
- **Passos:**  
  1. Fazer backup do DB (`pessoas_backup.db`).  
  2. Enviar payload 1 para `/login`.  
  3. Salvar saída (terminal) e resposta em `respostas/sql_injection/`.  
  4. Repetir com payloads 2 e 3.  
- **Resultado esperado (se vulnerável):** resposta retorna 200 e/ou dados de usuário mesmo com credenciais inválidas. Sessão criada.  
- **Evidências a salvar:** screenshot do terminal (`sql_injection_terminal.png`), arquivos de resposta (ex.: `sqli_or_true.txt`) e `resumo_sqli.txt` (conclusão).  
- **Critério de aceite:** demonstração clara (req + resp) provando acesso sem credenciais válidas.

---

### Caso 2 — SQL Injection (mensagens de erro / exposição de stack)
- **Objetivo:** identificar se a aplicação divulga mensagens de erro com detalhes da query ou stack.  
- **Endpoint alvo:** qualquer que aceite input direto em query (login, busca).  
- **Payloads:** strings que quebram a query, ex.: `"' OR 1=1; DROP TABLE pessoa; --"` ou `"' OR (select 1/0) --"`.  
- **Passos:** executar e observar status 500 ou HTML com trace. Salvar saída.  
- **Resultado esperado (vulnerável):** servidor retorna 500 com informação de erro (ex.: "sqlite3.OperationalError: no such table: pessoa" ou stack trace).  
- **Evidências:** salvar prints e respostas de erro seguindo mesma estrutura.

---

### Caso 3 — BOLA (Broken Object Level Authorization) — leitura indevida
- **Objetivo:** verificar se um usuário autenticado consegue acessar dados de outro usuário trocando o `id` no endpoint `GET /pessoas/<id>`.  
- **Pré-condição:** dois usuários no DB (ex.: `id=1` aluno, `id=19` professor).  
- **Passos:**  
  1. Login com usuário A (aluno). Salvar cookie/sessão.  
  2. `GET /pessoas/19` (ou id de outro usuário) usando a sessão do aluno.  
  3. Salvar resposta e terminal.  
- **Resultado esperado (vulnerável):** aluno consegue ver os dados do professor (status 200 com JSON de outra pessoa).  
- **Evidências:** `respostas/bola/get_pessoa_19_com_sessao_aluno.txt` e `relatorio/evidencias/bola/...`.

---

### Caso 4 — BOLA (alteração indevida)
- **Objetivo:** verificar se um usuário consegue modificar dados de outro usuário (`PUT /pessoas/<id>`).  
- **Passos:**  
  1. Fazer login como Aluno.  
  2. `PUT /pessoas/19` com payload que altera campos (ex.: `perfil`, `senha`, `nome`).  
  3. Observar status code e corpo. Verificar se a alteração persistiu (`GET /pessoas/19`).  
- **Resultado esperado (vulnerável):** alteração aceita com status 200.  
- **Evidências:** salvar request/response e resumo.

---

### Caso 5 — Elevação de Privilégios (Privilege Escalation)
- **Objetivo:** testar se um usuário sem privilégios consegue escalar seu perfil (ex.: aluno -> professor) ou criar usuário com perfil elevado.  
- **Caminhos a testar:**  
  1. `PUT /pessoas/<meu_id>` tentando alterar `perfil` do próprio usuário para `Professor`.  
  2. `POST /pessoas` criando um novo usuário com `perfil: "Professor"` usando credenciais de aluno.  
- **Passos:**  
  1. Autenticar como aluno; executar `PUT /pessoas/<aluno_id>` com payload contendo `"perfil": "Professor"`.  
  2. Salvar resposta (se 403 => controle está funcionando; se 200 => vulnerabilidade).  
  3. Tentar `POST /pessoas` com payload de criação de usuário professor (ver se endpoint existe e aceita).  
- **Resultado esperado (vulnerável):** servidor aceita alteração/criação sem autorização (200 ou 201).  
- **Evidências:** `respostas/privilege_escalation/update_user_as_aluno.txt`, `create_user_as_aluno.txt`, screenshot e resumo.

---

### Caso 6 — Broken Function Level Authorization (BFLA)
- **Objetivo:** identificar funções/endpoints que deveriam ser restritos a determinados perfis (ex.: `/admin/*`, `/pessoas/ativar`) mas que qualquer usuário autenticado consegue executar.  
- **Passos:**  
  1. Listar rotas (use `scripts/list_routes.py`) e identificar endpoints sensíveis (`/pessoas/<id>/ativar`, `/pessoas/<id>/desativar`, etc).  
  2. Autenticar como usuário com perfil baixo (aluno) e tentar executar cada endpoint sensível.  
  3. Registrar status codes: 200 = potencial vulnerabilidade; 403/401 = controle presente.  
- **Evidências:** salvar uma tabela no `resumo_bfla.txt` com cada endpoint testado, método, payload, resultado e conclusão.

---

## Checklist antes de gerar evidências finais (PDF)
- [ ] Revisar que todas as evidências estejam em `relatorio/evidencias/<categoria>/` com nomes padronizados.  
- [ ] Remover arquivos temporários que não sejam parte da evidência final (ex.: logs irrelevantes).  
- [ ] Incluir um `resumo_geral.pdf` ou `resumo_geral.md` que traga: objetivo, metodologia, cada vulnerabilidade encontrada (ou não encontrada), risco e recomendação de correção.  
- [ ] Se nenhum caminho explorado mostrou vulnerabilidade (ex.: `POST /pessoas` retornou 404), documentar que o endpoint não existe ou não é vulnerável naquele fluxo. Isso também é evidência.

---
