# Aplicação de pessoas do curso


## ⚙️ Configuração do Ambiente

Crie um ambiente virtual

```bash
python -m venv venv
```

Ative o ambiente virtual

Linux
```bash
source venv/bin/activate
```

Windows
```bash
venv\\Scripts\\activate 
```

Instale as dependências

```bash
pip install -r requirements.txt
```

## 🚀 Executando a Aplicação

Inicialize o banco de dados

```bash
python init_db.py
```

Execute a API

```bash
python routes.py
```

## 🌐 Acessando a API
A API estará disponível em http://localhost:5000 com os seguintes endpoints:

Endpoints Principais:

| Método | Endpoint | Descrição |
|---|---|---|
| POST | /login | Login |
| GET | /pessoas/<id> | Busca pessoa |
| PUT | /pessoas/<id> | Atualiza dados |
| POST | /pessoas/<id>/desativar | Desativa usuário |