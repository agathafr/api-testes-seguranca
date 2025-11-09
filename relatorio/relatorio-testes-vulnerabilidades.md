# 🧪 Relatório de Testes de Segurança da API Flask

Este relatório documenta a execução prática de testes de segurança realizados na API Flask conforme os requisitos da atividade **"Prática de Testes de Segurança"**, abordando as seguintes vulnerabilidades conhecidas:

- **SQL Injection (SQLi)**
- **Broken Object Level Authorization (BOLA)**
- **Elevação de Privilégios**
- **Broken Function Level Authorization (BFLA)**

Cada seção descreve os cenários testados, resultados observados, análise técnica e conclusão, acompanhados das evidências armazenadas na pasta `relatorio/evidencias/`.

---

## 📑 Índice

- [1. SQL Injection (SQLi)](#1-sql-injection-sqli)
- [2. Broken Object Level Authorization (BOLA)](#2-broken-object-level-authorization-bola)
- [3. Elevação de Privilégios](#3-elevação-de-privilégios)
- [4. Broken Function Level Authorization (BFLA)](#4-broken-function-level-authorization-bfla)

---
# 1. SQL Injection (SQLi)  
fileciteturn62file0

---

## 🎯 Objetivo
Testar, validar e classificar a presença de vetores de **SQL Injection (SQLi)** nos endpoints principais da API (`POST /login`, `GET /pessoas/<id>`, `PUT /pessoas/<id>`), aplicando técnicas distintas: *error-based*, *boolean blind*, *time-based*, *UNION-based (exfiltrate)* e injeção via corpo (PUT). O objetivo é produzir provas (evidências) e recomendações práticas para correção.

---

## ⚙️ Escopo — cenários executados

| Nº | Cenário (script) | Endpoint / Método | Técnica testada |
|---:|------------------:|-------------------|-----------------:|
| 1 | `sql_error_based.py` | `GET /pessoas/{id}` | Error-based (forçar/observar erros) |
| 2 | `sql_get_pessoa_sqli.py` | `GET /pessoas/{id}` | Injeção via path/ID |
| 3 | `sql_login_bypass_auth.py` | `POST /login` | Bypass (tautology / authentication bypass) |
| 4 | `sql_login_union_exfiltrate.py` | `POST /login` | UNION-based / exfiltração (detecção de colunas + subqueries) |
| 5 | `sql_login_union_exfiltrate_var.py` | variações | Ajustes iterativos do cenário 4 |
| 6 | `sql_put_injection.py` | `PUT /pessoas/{id}` | Injection em payload JSON (update) |
| 7 | `sql_time_based.py` | `GET /pessoas/{id}` | Time-based blind (heurístico para SQLite) |
| 8 | `sql_boolean_blind.py` / `sql_boolean_blind_improved.py` | `POST /login` | Boolean blind (inferência por diferenças) |

> Observação: cada script grava um arquivo `.txt` em `respostas/sql_injection/cenarios/<nome_do_cenario>/` com timestamp. Esses `.txt` servem como evidência bruta.

---

## 📊 Resultados consolidados (resumo por cenário)

> Nota: “Detectada” = evidência suficiente (response/erro/exfiltração). “Inconclusivo” = testes atuais não produziram prova definitiva.

| Cenário | Objetivo | Evidência (.txt) | Interpretação rápida | Status |
|---|---|---:|---|---:|
| `sql_error_based.py` | Forçar erro para obter info | `respostas/sql_injection/cenarios/sql_error_based/...` | Aparecimento de mensagens/indicadores de erro — indica exposição de informações; não houve exfiltração direta nos testes. | Inconclusivo / info-leak (logs) |
| `sql_boolean_blind_improved.py` / `v2` | Boolean blind via `/login` | `respostas/sql_injection/cenarios/sql_boolean_blind_improved...` | Extração parcial: primeiras posições do campo `login` inferidas com consistência (PoC parcial). | Parcial / Promissor |
| `sql_get_pessoa_sqli.py` | Injeção via path/ID | `respostas/sql_injection/cenarios/sql_get_pessoa_sqli/...` | Comportamento diferencial ao variar `id`/payload → indicativo de montagem insegura do `id`. | Indicativo |
| `sql_login_bypass_auth.py` | Bypass de autenticação | `respostas/sql_injection/cenarios/sql_login_bypass_auth/...` | Tautologias e payloads similares resultaram em login válido (200) — PoC de bypass observada. | Alto risco (PoC confirmada) |
| `sql_login_union_exfiltrate.py` | UNION exfiltration | `respostas/sql_injection/cenarios/sql_login_union_exfiltrate/...` | Erros `UNION` mismatch inicialmente; após calibragem (colunas e padding) foi possível obter valores injetados (exfiltração parcial). | Exploitable (ajuste requerido) |
| `sql_put_injection.py` | PUT /pessoas/<id> | `respostas/sql_injection/cenarios/sql_put_injection/...` | PUT permitiu alterações legítimas e tentativa de injeção foi testada; ownership e validação parcimoniosas. | Médio (controle insuficiente) |
| `sql_time_based.py` | Time-based blind | `respostas/sql_injection/cenarios/sql_time_based/...` | Heurística com `randomblob()` e amostragem; variações de tempo foram medidas mas não houve exfiltração clara com os payloads testados. | Inconclusivo / experimentar com maior amostragem |

---

## 🔎 Análise por cenário (detalhada e recomendações)

### `sql_error_based.py` — Error-based
**O que vimos:** respostas e logs apresentaram mensagens/indicadores relacionados ao banco (strings tipo “sqlite”, “syntax error”, tracebacks em ambiente de desenvolvimento).  
**Risco:** exposição de informações internas facilita tuning de payloads e descoberta de estrutura.  
**Recomendação:** remover/ocultar stack traces do cliente; usar logging interno; parametrizar queries; não retornar erros de DB ao usuário.

---

### `sql_boolean_blind_improved.py` / `v2` — Boolean blind (via POST /login)
**O que vimos:** ao direcionar injeções para o campo `login` do `POST /login`, com amostragem e heurísticas (mediana dos tempos, status e tamanho da resposta), foi possível inferir de forma consistente as primeiras posições do campo alvo (PoC parcial: primeiros 3 caracteres confirmados nos testes).  
**Risco:** alto se o canal for completável (permite extração caractere a caractere).  
**Recomendação:**  
- Prioridade: parametrizar as queries do login (Prepared Statements).  
- Mitigação adicional: limitar tentativas (rate-limit), monitorar padrões (muitos requests / mesmas rotas), e normalizar respostas para reduzir sinais diferenciais (tornar respostas mais homogêneas quanto a tempo/status).

---

### `sql_get_pessoa_sqli.py` — Injeção via path/ID
**O que vimos:** variações do ID produziram diferenças no comportamento (404 / 401), o que sugere que o ID pode estar sendo concatenado em SQL sem sanitização.  
**Risco:** se `id` for concatenado, pode permitir extração e manipulação.  
**Recomendação:** validar/forçar o tipo (cast para int), usar ORM/queries parametrizadas e implementar checagens de autorização por recurso.

---

### `sql_login_bypass_auth.py` — Bypass de autenticação (tautology)
**O que vimos:** payloads tautológicos (`' OR '1'='1`) ou similares resultaram em login bem-sucedido (sessão criada) em testes — PoC prática de bypass.  
**Risco:** crítico — permite autenticação sem credenciais válidas.  
**Recomendação URGENTE:** substituir concatenação por consultas parametrizadas; validar senhas com hashing (bcrypt/werkzeug.generate_password_hash já presente, mas verifique uso correto); aplicar checagem adicional antes de setar sessão.

---

### `sql_login_union_exfiltrate.py` / variantes — UNION exfiltration
**O que vimos:** inicialmente erros de mismatch de colunas; com detecção automática de colunas (teste incremental) e padding com `NULL`/expressões, foi possível inserir valores e visualizar conteúdos retornados — proving exfiltration possible. Também observou-se erros típicos a evitar (multistatement).  
**Risco:** alto — exfiltração direta de colunas (incl. `senha` se presente em texto) é possível.  
**Recomendação:** parametrizar queries; limitar colunas retornadas; evitar que campos arbitrários sejam refletidos sem validação; tratar entradas como dados não como código.

---

### `sql_put_injection.py` — PUT / atualização
**O que vimos:** operações PUT permitiram alterar campos (nome/perfil). Tentativas de alterar outro usuário retornaram 403 em parte dos testes, indicando algum controle de ownership, mas não foi consistente para todos os vetores testados. Tentativas de payloads potencialmente destrutivos foram registradas e não necessariamente executadas (graças ao backup/restores).  
**Risco:** médio; possível escalonamento se combinação com falha de autorização.  
**Recomendação:** reforçar verificação server-side de ownership/role antes de aplicar updates; validar conteúdo dos campos; parametrizar queries.

---

### `sql_time_based.py` — Time-based blind (heurístico para SQLite)
**O que vimos:** testes com `randomblob()` e amostragem mostraram variação nas médias, mas não produziram exfiltração clara com os parâmetros atuais. Time-based em SQLite local pode ser ruidoso e custoso.  
**Risco:** baixo-médio; aplicável, mas normalmente mais lento e ruidoso que UNION/boolean.  
**Recomendação:** só usar como fallback quando UNION/boolean não forem viáveis; aumentar amostras e calibrar thresholds se for necessário.

---

## 📂 Evidências geradas (arquivos `.txt`)
- `respostas/sql_injection/cenarios/sql_error_based/sql_error_based_<timestamp>.txt`  
- `respostas/sql_injection/cenarios/sql_get_pessoa_sqli/sql_get_pessoa_sqli_<timestamp>.txt`  
- `respostas/sql_injection/cenarios/sql_login_bypass_auth/sql_login_bypass_auth_<timestamp>.txt` — **bypass observado**  
- `respostas/sql_injection/cenarios/sql_login_union_exfiltrate/sql_login_union_exfiltrate_<timestamp>.txt` — detecção de colunas / exfiltração parcial  
- `respostas/sql_injection/cenarios/sql_login_union_exfiltrate_var/sql_login_union_exfiltrate_var_<timestamp>.txt` — variações iterativas  
- `respostas/sql_injection/cenarios/sql_put_injection/sql_put_injection_<timestamp>.txt`  
- `respostas/sql_injection/cenarios/sql_time_based/sql_time_based_<timestamp>.txt`  
- `respostas/sql_injection/cenarios/sql_boolean_blind_improved/sql_boolean_blind_improved_<timestamp>.txt` (e _v2) — inferências parciais

> **Anexo recomendado no relatório final:** copiar trechos relevantes de cada `.txt` (payloads que produziram 200, outputs JSON com valores injetados ou mensagens de erro úteis) e incluir prints de terminal / trechos do `routes.py` que ilustrem onde a concatenação/raw SQL ocorre (por exemplo no `POST /login`).

---

## ✅ Conclusão consolidada (resumo executivo)
1. **Vulnerabilidades confirmadas / de maior risco**
   - **Authentication bypass** via injeção no `POST /login` — PoC observada; correção prioritária.  
   - **UNION-based exfiltration** é possível após calibragem (detecção de nº de colunas e padding) — risco alto de exposição de dados.  
2. **Vulnerabilidades confirmed / de média prioridade**
   - Falha de validação/ownership em `PUT /pessoas/<id>` — risco de alteração indevida.  
3. **Mecanismos de mitigação recomendados (curto prazo)**
   - **Parametrizar todas as consultas** (prepared statements / ORM parametrizado).  
   - **Remover exposição de tracebacks** ao cliente; logar internamente.  
   - **Forçar tipos e validar inputs** (cast/parse dos IDs).  
   - **Rate limiting / WAF rules** para rotas críticas (/login, /pessoas/*).  
   - **Monitoramento e detecção** de padrões anômalos (muitos requests sequenciais com payloads similares).

---

## Conclusões (síntese)
- Há **indícios fortes** de vulnerabilidade em pontos cruciais:
  - **Bypass de autenticação (login)** — `sql_login_bypass_auth.py` gerou comportamento que sugere SQL concatenado no endpoint de login. Recomendação: corrigir login para queries parametrizadas e revisar como as credenciais são validadas.
  - **UNION exfiltration** — `sql_login_union_exfiltrate` e sua variante mostram que, com ajustes no número de colunas/tipo, há chance real de exfiltrar dados. Recomendação: parametrizar, restringir colunas e suprimir erros sensíveis.
  - **PUT / alteração de registros** — `sql_put_injection.py` demonstrou alteração possível do próprio perfil (e possíveis falhas de autorização), caracterizando BOLA. Recomendação: checar ownership/role no servidor e parametrizar queries.
- Outros cenários (boolean blind, time-based, error-based) forneceram **evidências parciais** ou foram inconclusivos, porém mostraram que a aplicação loga erros do DB (tracebacks), o que é risco adicional (informação sensível em logs).

---

## Riscos e impacto
- Exfiltração de dados sensíveis (login, emails, perfis) via SQLi → violação de privacidade e requisitos legais.  
- Bypass de autenticação → acesso não autorizado a funcionalidades/recursos.  
- Modificação de dados (PUT) sem autorização → integridade comprometida.  
- Exposição de mensagens de erro nos logs → informações para escalada de ataque.

---

## Recomendações de correção (prioritárias)
1. **Parâmetros e Prepared Statements:** substituir todas as consultas que concatenam inputs por queries parametrizadas ou usar o ORM com binding de parâmetros.  
2. **Validação estrita de entrada:** aplicar validação de tipo (ex.: forçar `id` a inteiro) e sanitização em todas as entradas recebidas por path, query, body.  
3. **Controle de autorização robusto:** no PUT/updates, checar que o `user_id` autenticado tem permissão de editar o recurso; permitir edição apenas se proprietário ou role admin.  
4. **Tratamento de erros seguro:** capturar `sqlite3.OperationalError` e retornar JSON 4xx/5xx controlado (evitar tracebacks públicos) — logar internamente.  
5. **Remover mensagens sensíveis dos logs:** evitar expor DDL/queries completas em logs acessíveis.  
6. **Rate limiting + WAF:** aplicar limites e regras para mitigar ataques automatizados de injeção e enumeração.  
7. **Testes e verificação:** após correção, executar os mesmos scripts de PoC para verificar que não há mais exfiltração ou bypass.

---

### 📂 Evidências

As evidências completas estão disponíveis em:  
>`relatorio/evidencias/sql_injection/cenarios/`

Cada subpasta contém:
- Arquivo `.txt` com o retorno detalhado das requisições;  
- Capturas de tela (`.png`) mostrando a execução dos testes e os status HTTP observados.

---

## 2. Broken Object Level Authorization (BOLA)

### 🎯 Objetivo
Avaliar se a aplicação implementa corretamente o controle de acesso a objetos, impedindo que um usuário acesse recursos que não lhe pertencem — por exemplo, consultar dados de outro usuário através de manipulação direta do identificador (`id`) em endpoints REST.

---

### ⚙️ Escopo dos testes

Foram desenvolvidos **4 cenários automatizados** para avaliar o comportamento da API quanto ao controle de acesso por objeto:

| Nº | Cenário | Perfil | Método | Endpoint | Resultado esperado |
|----:|----------|---------|---------|-----------|----------------------|
| 1 | Consultar **próprio** usuário | Aluno | GET | `/pessoas/{id}` | 200 (permitido) |
| 2 | Consultar **outro** usuário | Aluno | GET | `/pessoas/{id}` | 403 (bloquear acesso a terceiros) |
| 3 | Consultar **outro** usuário | Professor | GET | `/pessoas/{id}` | 200 (vulnerabilidade BOLA) |
| 4 | Consultar **usuário com ID válido** sem autenticação | Anônimo | GET | `/pessoas/{id}` | 401 (bloquear acesso anônimo) |

> 📁 As evidências estão salvas em:
> - `relatorio/evidencias/bola/cenarios/...`

---

### 📊 Resultados obtidos

| Cenário | Perfil | Status HTTP | Resultado observado | Interpretação |
|----------|---------|:-----------:|---------------------|---------------|
| 1 | Aluno (próprio) | 200 | Retornou dados do próprio usuário | ✅ Proteção correta |
| 2 | Aluno (outro) | 200 | Retornou dados de outro usuário | ⚠️ Vulnerabilidade BOLA |
| 3 | Professor (outro) | 200 | Retornou dados de outro usuário | ⚠️ Vulnerabilidade BOLA |
| 4 | Anônimo | 401 | Acesso negado | ✅ Proteção aplicada |

---

### 🧠 Análise técnica

Durante os testes, observou-se que a API **não valida se o `id` requisitado pertence ao usuário autenticado**.  
Dessa forma, um aluno ou professor autenticado pode modificar o parâmetro `{id}` na URL (`/pessoas/{id}`) e visualizar dados de outras contas.

Exemplo real observado:

```bash
# Login como Aluno A (id=1)
GET /pessoas/2 → 200 OK
{
  "id": 2,
  "login": "1393033@sga.pucminas.br",
  "nome": "Beatriz Fassani Paschoal",
  "perfil": "Aluno"
}
```

Esse comportamento viola o princípio de **Autorização por Objeto** (Object-Level Authorization), uma das vulnerabilidades mais críticas no OWASP API Top 10 (API1:2023).

---

### 🧩 Conclusão revisada — Vulnerabilidade confirmada

O controle de autorização por objeto não está sendo aplicado de forma consistente.  
A aplicação deveria validar se o `id` solicitado corresponde ao usuário autenticado antes de retornar dados sensíveis.

Portanto, foram identificadas as seguintes vulnerabilidades:

| Endpoint | Perfil | Método | Status | Classificação |
|-----------|---------|---------|---------|----------------|
| `/pessoas/{id}` | Aluno | GET | 200 | ⚠️ BOLA confirmada |
| `/pessoas/{id}` | Professor | GET | 200 | ⚠️ BOLA confirmada |

---

### 🔐 Impactos potenciais

- **Exposição de dados pessoais:** qualquer aluno pode acessar dados de outro usuário.  
- **Quebra de privacidade:** vazamento de nomes, e-mails e perfis.  
- **Comprometimento de compliance:** risco de não conformidade com LGPD.  

---

### 💡 Recomendações

1. **Aplicar checagem de propriedade** nos endpoints sensíveis (`/pessoas/{id}`), validando se o `id` pertence ao usuário autenticado.  
2. **Utilizar o identificador da sessão (`session['user_id']`)** como base para consultas seguras.  
3. **Restringir retornos de dados** apenas ao próprio perfil, a menos que o papel (ex: admin) tenha permissão explícita.  
4. **Adicionar testes automatizados de BOLA** nos pipelines CI/CD.

---

### 📘 Consolidação final — BOLA

| Verificação | Resultado | Evidência |
|--------------|------------|-----------|
| Autenticação obrigatória | ✅ Ok | Anônimo → 401 |
| Controle de propriedade aplicado | ⚠️ Parcial | Aluno/Professor → 200 |
| Exposição de dados de terceiros | ⚠️ Detectada | Retorno de dados de outro usuário |
| Regra de acesso consistente | ⚠️ Parcial | Depende do perfil |

**Conclusão geral:**  
Os testes confirmaram **Broken Object Level Authorization (BOLA)**, pois usuários autenticados conseguem visualizar dados de outros perfis sem validação de propriedade.  
Embora o controle de autenticação esteja presente, **a autorização por objeto está falhando**, configurando vulnerabilidade crítica conforme **OWASP API1:2023**.

---

### 📂 Evidências

As evidências completas estão disponíveis em:  
>`relatorio/evidencias/bola/cenarios/`

Cada subpasta contém:
- Arquivo `.txt` com o retorno detalhado das requisições;  
- Capturas de tela (`.png`) mostrando a execução dos testes e os status HTTP observados.

---
## 3. Elevação de Privilégios

### 🎯 Objetivo
Verificar se a aplicação impede que usuários com menor privilégio elevem seu próprio perfil ou elevem o privilégio de outros perfis (por exemplo, transformar um *Aluno* em *Professor*), bem como se usuários anônimos conseguem executar operações que alterem perfis/privilegios.

---

### ⚙️ Escopo dos testes (cenários implementados)

Os cenários automatizados implementados para esta seção foram (pastas: `testes/seguranca/elevacao_privilegios/cenarios` e evidências em `relatorio/evidencias/`):

1. `aluno_put_elevar_proprio_perfil.py` — Aluno tenta alterar seu próprio `perfil` para outro com maior privilégio.  
2. `aluno_put_elevar_outro_perfil.py` — Aluno tenta alterar o `perfil` de OUTRO usuário.  
3. `professor_put_elevar_outro_perfil.py` — Professor tenta alterar o `perfil` de OUTRO usuário.  
4. `professor_put_elevar_proprio_perfil.py` — Professor tenta alterar seu próprio perfil (cenário observado quando criado).  
5. `anonimo_put_elevar_qualquer_perfil.py` — Requisição anônima (sem login) tentando fazer `PUT /pessoas/{id}` com mudança de `perfil`.  

---

### 📊 Resultados consolidados 

| Nº | Cenário | Expectativa (segurança) | Resultado observado | Interpretação |
|----:|---------|--------------------------|---------------------|---------------|
| 1 | `aluno_put_elevar_proprio_perfil` | **Bloquear** (aluno **não** deve poder elevar-se) | **200** — PUT aplicado (evidência salva). | ⚠️ **Falha**: aluno conseguiu alterar seu próprio `perfil`. Possível elevação de privilégio local. |
| 2 | `aluno_put_elevar_outro_perfil` | **Bloquear** | **403** — Acesso negado. | ✅ Proteção aplicada contra alteração de terceiros por aluno. |
| 3 | `professor_put_elevar_outro_perfil` | **Bloquear** (somente admin deve) | **403** — Acesso negado. | ✅ Proteção aplicada (professor não elevou outro). |
| 4 | `professor_put_elevar_proprio_perfil` | Bloquear / sem sentido se já for perfil de maior privilégio | Comportamento observado: professor já era 'Professor' (nenhum ganho prático). | ⚪ Pode ser redundante — professor já tem maior privilégio; permitir alterar próprio perfil não necessariamente eleva além do que já tem. |
| 5 | `anonimo_put_elevar_qualquer_perfil` | **Bloquear** (401) | **401** — Acesso negado (sem login). | ✅ Proteção aplicada contra anônimo. |

**Resumo curto:** O caso mais crítico detectado foi o cenário (1) — **aluno** conseguiu alterar seu **próprio** `perfil` (PUT que retornou 200) em uma execução. Os demais cenários importantes (alteração de terceiros por aluno, ações anônimas, professor alterando terceiros) apresentaram bloqueio (403/401), conforme evidências geradas.

---

### 🧠 Análise técnica e causa provável

Ao inspecionar o código das rotas (`app/routes.py`) e os decoradores de autorização, as evidências apontam para dois problemas possíveis, combinados:

1. **Autorização insuficiente no endpoint de PUT `/pessoas/{id}`** — a checagem atual permite que o usuário altere seu próprio registro (isso é esperado), porém **não diferencia quais campos podem ser atualizados por cada papel**. Se não houver validação extra para o campo `perfil`, um usuário pode substituir `perfil` por um valor com maior privilégio.  
   - No código observamos: `if session['user_id'] != pessoa.id and Pessoa.query.get(session['user_id']).perfil != 'professor': return 403` — essa verificação permite edição própria, sem bloquear mudança do campo `perfil` por quem edita o próprio registro.
2. **Confusão entre "função administrativa" e "perfil"** — o decorador `@admin_required` atualmente checa se `perfil.lower() != 'professor'`, ou seja, considera `professor` como papel administrativo. Isso mistura papéis e aumenta risco de confusão ao validar quem pode fazer o quê.

**Consequência prática:** se o endpoint permite que um usuário edite livremente o campo `perfil` sobre o seu próprio registro, então um *Aluno* poderia, por via do PUT no próprio ID, alterar `perfil` para `Professor` (ou "Admin" se o sistema aceitar), obtendo assim maior poder funcional na aplicação — caracterizando **elevação de privilégios**.

---

### 🔐 Impactos potenciais (se explorado com sucesso)

- Usuário de nível baixo (aluno) consegue ganhar função/interesses operacionais que deveria ser exclusiva de administradores.  
- Acesso indevido a endpoints administrativos se o papel alterado permitir (ex.: ativar/desativar outros usuários).  
- Ruptura da garantia de segregação de funções (SoD) e potencial manipulação/ataque interno.  
- Problemas de auditoria e compliance (LGPD) pelo aumento indevido de alcance funcional.

---

### 💡 Recomendações imediatas (prioridade alta)

1. **Bloquear alteração do campo `perfil` via PUT por perfis não administrativos.** Permitir que um usuário edite somente campos não-privilegiados (nome, senha, etc.). Para alterar `perfil` crie um **endpoint administrativo** específico protegido por `@admin_required` real (ver ponto 2).  
2. **Corrigir `@admin_required`** para checar um papel realmente administrativo (ex.: `admin`, `system_admin`) em vez de `professor`, ou introduzir um RBAC explícito (roles = ['admin','professor','aluno']).  
3. **Validar e sanitizar o payload do PUT**: recusar mudanças no campo `perfil` quando quem faz a chamada não for administrador.  
4. **Adicionar teste automatizado que tenta alterar `perfil` via PUT no próprio ID** (cobertura regressiva) e bloquear regressões.  
5. **Adicionar logs de auditoria** para qualquer alteração de `perfil` ou demais campos sensíveis.  
6. **Revisão de acesso de produção**: garantir que ambientes reais não carreguem dados de teste com perfis ajustáveis.

---

### 📂 Evidências e local dos arquivos

- Scripts executados: `testes/seguranca/elevacao_privilegios/cenarios/*.py`  
- Evidências (`.txt` gerados automaticamente) em: `relatorio/evidencias/elevacao_privilegios/cenarios/`

---

## 4. Broken Function Level Authorization (BFLA)

### 🎯 Objetivo
Avaliar se a aplicação implementa corretamente o controle de acesso por função, garantindo que apenas perfis autorizados executem ações críticas — como ativar, desativar ou atualizar usuários — e que cada papel (anônimo, aluno, professor, admin) tenha acesso estritamente compatível com suas permissões.

---

### ⚙️ Escopo dos testes

Foram desenvolvidos e executados **12 cenários automatizados** abrangendo as principais combinações de papéis e endpoints administrativos:

| Nº | Perfil | Ação | Endpoint | Método | Resultado esperado |
|----:|---------|-------|-----------|---------|----------------------|
| 1 | **Anônimo** | Listar pessoas | `/pessoas` | GET | Bloquear (401) |
| 2 | **Anônimo** | Acessar funções administrativas | `/pessoas/<id>/ativar` / `/desativar` | POST | Bloquear (401 ou 405) |
| 3 | **Aluno** | Atualizar **próprio** usuário | `/pessoas/<id>` | PUT | Permitir apenas dados próprios |
| 4 | **Aluno** | Atualizar **outro** usuário | `/pessoas/<id>` | PUT | Bloquear (403) |
| 5 | **Professor** | Ativar outro usuário | `/pessoas/<id>/ativar` | POST | Bloquear (somente admin deveria) |
| 6 | **Professor** | Desativar outro usuário | `/pessoas/<id>/desativar` | POST | Bloquear (somente admin deveria) |
| 7 | **Professor** | Atualizar próprio usuário | `/pessoas/<id>` | PUT | Permitir |
| 8 | **Professor** | Atualizar outro usuário | `/pessoas/<id>` | PUT | Bloquear |
| 9 | **Admin** | Ativar outro usuário | `/pessoas/<id>/ativar` | POST | Permitir |
| 10 | **Admin** | Desativar outro usuário | `/pessoas/<id>/desativar` | POST | Permitir |
| 11 | **Admin** | Atualizar outro usuário | `/pessoas/<id>` | PUT | Permitir |
| 12 | **Admin** | Atualizar próprio usuário | `/pessoas/<id>` | PUT | Permitir |

> 📁 As evidências correspondentes a cada cenário estão salvas em:
> - `relatorio/evidencias/bfla/cenarios/...`

---

### 📊 Resultados obtidos

| Cenário | Perfil | Status HTTP | Resultado observado | Interpretação |
|----------|---------|:-----------:|---------------------|---------------|
| 1 | Anônimo | 401 / 404 | Acesso negado | ✅ Proteção correta |
| 2 | Anônimo | 405 | Método não permitido | ✅ Proteção correta |
| 3 | Aluno | 200 | Atualizou dados próprios | ✅ Correto |
| 4 | Aluno | 403 | Acesso negado a outro ID | ✅ Correto |
| 5 | Professor | 200 | Acesso permitido | ⚠️ Vulnerabilidade BFLA |
| 6 | Professor | 200 | Acesso permitido | ⚠️ Vulnerabilidade BFLA |
| 7 | Professor | 200 | Atualizou dados próprios | ✅ Correto |
| 8 | Professor | 403 | Acesso negado a outro ID | ✅ Correto |
| 9 | Admin | 200 | Acesso permitido | ✅ Correto |
| 10 | Admin | 200 | Acesso permitido | ✅ Correto |
| 11 | Admin | 200 | Atualizou outro usuário | ✅ Correto |
| 12 | Admin | 200 | Atualizou próprio usuário | ✅ Correto |

---

### 🧠 Análise técnica

Durante a inspeção do código, foi identificado que o decorador `@admin_required` realiza a seguinte checagem:

```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = Pessoa.query.get(session['user_id'])
        if not user or user.perfil.lower() != 'professor':
            return jsonify({"error": "Acesso negado. Permissão insuficiente."}), 403
        return f(*args, **kwargs)
    return decorated_function
```

Esse trecho evidencia que **o sistema autoriza apenas usuários com o perfil “professor”** a executar funções que deveriam ser administrativas — como ativar e desativar contas — o que **viola o princípio do menor privilégio** e **caracteriza Broken Function Level Authorization (BFLA)**.

Na prática, qualquer professor autenticado pode executar ações de alto impacto sobre outros usuários, inclusive administradores ou alunos, sem restrições adicionais.

---

### 🧩 Conclusão revisada — Vulnerabilidade confirmada

Embora não haja documentação formal sobre a hierarquia de papéis, o bom senso de segurança indica que ações de **ativar e desativar contas** devem ser exclusivas de perfis administrativos.

O comportamento observado demonstra que **o controle de função está incorreto**, permitindo que um usuário de nível intermediário (professor) exerça funções de administração.

Portanto, **os endpoints abaixo foram classificados como vulneráveis**:

| Endpoint | Método | Perfil | Status | Classificação |
|-----------|---------|---------|---------|----------------|
| `/pessoas/{id}/ativar` | POST | Professor | 200 | ⚠️ BFLA confirmada |
| `/pessoas/{id}/desativar` | POST | Professor | 200 | ⚠️ BFLA confirmada |

---

### 🔐 Impactos potenciais

- **Elevação indevida de privilégio funcional:** Professores podem ativar/desativar qualquer conta.  
- **Ausência de segregação de funções:** Falta de distinção clara entre funções administrativas e operacionais.  
- **Comprometimento da disponibilidade:** Um professor mal-intencionado pode desativar contas legítimas.  
- **Superfície de ataque ampliada:** O controle inadequado permite manipulação de estados de usuários.

---

### 💡 Recomendações

1. **Revisar o decorador `@admin_required`**, garantindo que apenas perfis realmente administrativos possam executar ações sensíveis.  
2. **Implementar um modelo RBAC (Role-Based Access Control)** com separação clara de papéis.  
3. **Adicionar logs de auditoria** para todas as operações de ativação/desativação de contas.  
4. **Automatizar testes de autorização** em pipelines CI/CD, assegurando que regressões de segurança sejam detectadas em futuras versões.  

---

### 📘 Consolidação final — BFLA

| Verificação | Resultado | Evidência |
|--------------|------------|-----------|
| Autenticação obrigatória nas rotas sensíveis | ✅ Ok | Anônimo → 401/405 |
| Controle de função aplicado corretamente | ⚠️ Parcial | Professor → 200 |
| Regra de propriedade no PUT | ✅ Ok | 403 em edições de terceiros |
| Acesso indevido a funções críticas | ⚠️ Detectado | Ativar/Desativar → 200 |
| Controle de método HTTP | ✅ Ok | Respostas 405 corretas |

**Conclusão geral:**  
Os testes de BFLA demonstraram que a aplicação **não diferencia adequadamente papéis funcionais e administrativos**, permitindo que o perfil *professor* exerça ações críticas.  
Esse comportamento caracteriza **Broken Function Level Authorization (BFLA)** conforme **OWASP API4:2023**.  
Embora o sistema apresente boa proteção para ações de leitura e atualização de dados próprios, os controles de autorização em funções administrativas **devem ser aprimorados com urgência.**

---

### 📂 Evidências

As evidências de execução e respostas das requisições estão armazenadas em:  
>`relatorio/evidencias/bfla/cenarios/`  
>
>Cada subpasta contém:
>- Arquivo `.txt` com **status, headers e body** das respostas HTTP;
>- Captura de tela (`.png`) com o print do terminal durante a execução.

