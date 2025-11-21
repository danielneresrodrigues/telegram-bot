# Telegram Bot - Envio de Mensagens

Bot simples para envio automático de mensagens do Telegram a partir de filas no PostgreSQL.

## Requisitos

- Python 3.9+
- PostgreSQL
- Conta Telegram com bot criado via @BotFather

## Configuração

### 1. Criar as tabelas no PostgreSQL
```sql
CREATE TABLE "group" (
    group_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    group_id BIGINT NOT NULL,
    CONSTRAINT fk_group
        FOREIGN KEY(group_id) 
        REFERENCES "group"(group_id)
        ON DELETE CASCADE
);

CREATE TABLE message_poison (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    group_id BIGINT NOT NULL,
    info TEXT
);
```

### 2. Configurar ambiente virtual
```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
TOKEN=seu_token_do_telegram_aqui
host=localhost
database=telegram
user=postgres
password=root
```

**Como obter o TOKEN:**
1. Abra o Telegram e fale com @BotFather
2. Envie `/newbot` e siga as instruções
3. Copie o token fornecido

**Como descobrir o group_id:**
1. Adicione o bot ao grupo desejado
2. Envie uma mensagem no grupo
3. Acesse: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Procure por `"chat":{"id":-1001234567890` - esse é o group_id

## Uso

### Inserir mensagens no banco
```sql
-- Inserir grupo
INSERT INTO "group" (group_id, name) VALUES (-1001234567890, 'Meu Grupo');

-- Inserir mensagem
INSERT INTO message (message, group_id) VALUES ('Texto da mensagem', -1001234567890);
```

### Rodar o bot
```bash
python enviar_mensagens.py
```

O bot vai:
- Checar a tabela `message` a cada 5 segundos
- Enviar mensagens pendentes
- Deletar mensagens enviadas com sucesso
- Mover mensagens com erro para `message_poison`

## Estrutura
```
telegram/
├── enviar_mensagens.py   # Script principal
├── requirements.txt       # Dependências
├── .env                   # Configurações (não commitar!)
└── README.md             # Este arquivo
```

## Notas

- Adicione `.env` ao `.gitignore` para não expor credenciais
- O bot processa mensagens em ordem de inserção
- Mensagens com erro são movidas para `message_poison` para debug