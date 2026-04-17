# Argus Dashboard

Dashboard web interativo do projeto Argus com autenticação por login.

## Estrutura

```
dashboard/
├── app.py              Dashboard principal (Streamlit)
├── dados.py            Camada de acesso ao SQL Server
├── autenticacao.py     Sistema de login
└── requirements.txt    Dependências
```

## Como rodar localmente

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

O dashboard abre no navegador em http://localhost:8501

## Configuração do .env

Além das variáveis do pipeline principal, adicione:

```
DASH_USERS=admin:senha123,comercial:senha456
```

Formato: `usuario:senha` separado por vírgula.

## Como compartilhar o link com senha

1. Crie os usuários no `.env`
2. Rode o dashboard
3. Compartilhe o link com quem você quer dar acesso
4. Envie o usuário e senha em canal privado

Cada pessoa vai receber suas próprias credenciais.