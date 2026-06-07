# AgentamentoSystem

Sistema web de agendamento para salão/studio, desenvolvido com **Django 6**. Permite cadastro de clientes e profissionais, escolha de data/horário, confirmação de serviços e dashboards para acompanhamento dos atendimentos.

Repositório: [github.com/isaiasp7/Course_Django](https://github.com/isaiasp7/Course_Django)

---

## Requisitos

| Requisito | Versão recomendada |
|-----------|-------------------|
| Python | 3.12 ou superior |
| pip | incluso com o Python |
| Git | qualquer versão recente |

> Django 6 exige Python 3.12+. Em ambiente de desenvolvimento, o projeto foi testado com Python 3.13.

---

## Estrutura do repositório

```
Course_Django/                 ← raiz do clone (git)
├── AgentamentoSystem/         ← projeto Django (manage.py fica aqui)
│   ├── AgentamentoSystem/     ← settings, urls, wsgi
│   └── Apps/
│       ├── accounts/          ← login, cadastro, perfil
│       ├── appointments/      ← fluxo de agendamento
│       ├── dashboard/         ← painéis cliente e profissional
│       └── schedules/
├── requirements.txt
├── migrate.bat                ← atalho Windows para migrate
└── runserver.bat              ← atalho Windows para runserver
```

---

## Instalação passo a passo

### 1. Clonar o repositório

```bash
git clone https://github.com/isaiasp7/Course_Django.git
cd Course_Django
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell ou CMD):**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Com o ambiente ativo, o prompt deve mostrar `(.venv)`.

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Isso instala o Django 6.0.4 e dependências (`asgiref`, `sqlparse`, `tzdata`).

### 4. Entrar na pasta do projeto Django

```bash
cd AgentamentoSystem
```

Todos os comandos `manage.py` abaixo devem ser executados **dentro** desta pasta.

### 5. Aplicar migrações do banco de dados

O projeto usa **SQLite**. O arquivo `db.sqlite3` é criado automaticamente na pasta `AgentamentoSystem/` após a primeira migração.

```bash
python manage.py migrate
```

**Windows (alternativa):** na raiz do clone, dê duplo clique em `migrate.bat` ou execute:

```cmd
migrate.bat
```

### 6. (Opcional) Criar usuário do Django Admin

Para gerenciar serviços e agendamentos pelo painel administrativo:

```bash
python manage.py createsuperuser
```

Siga as instruções no terminal (usuário, e-mail e senha).

### 7. Iniciar o servidor de desenvolvimento

```bash
python manage.py runserver 0.0.0.0:8000
```

**Windows (alternativa):** na raiz do clone, execute `runserver.bat`.

Acesse no navegador:

| Página | URL |
|--------|-----|
| Início (redireciona para login) | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Cadastro de cliente | http://127.0.0.1:8000/accounts/cadastro/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

Para encerrar o servidor, pressione `Ctrl+C` no terminal.

---

## Deixar pronto para testar

O sistema não vem com usuários pré-cadastrados. Siga este roteiro mínimo:

### A. Cadastrar um profissional

1. Acesse a tela de login > Click em 'Sou um Profissional' 
2. Informe o código de acesso: **`STUDIO-PRO-2026`**
3. Complete o cadastro na tela seguinte.
   ex: *Nome Completo*: Jose Carlos
       *Email* : jose432@gmail.com
       *Telefone*: 88981329410
       *Senha* : 56845795sdk
       *Confirmar Senha* : 56845795sdk
4. Após o cadastro, faça login com o e-mail e senha criados — você será direcionado ao dashboard profissional.

> **Importante:** é necessário ter pelo menos **um profissional** cadastrado para que clientes consigam confirmar agendamentos.

### B. Cadastrar um cliente

1. Acesse a tela de Login, click em 'criar conta'
2. Preencha nome, e-mail, telefone e senha.
    ex: *Nome Completo*: Maurilio Consalves
        *Email* : Consalves456@gmail.com
        *Telefone*: 13858829410
        *Senha* : MC56845sdk
        *Confirmar Senha* : MC56845sdk
3. Faça login com os dados cadastrados.
4. Após o login, o cliente é enviado ao fluxo de agendamento.

### C. (Opcional) Cadastrar serviços pelo Admin

Se quiser serviços fixos antes de agendar:

1. Acesse http://127.0.0.1:8000/admin/ (com o superusuário criado no passo 6).
2. Em **Servicos**, adicione itens como *Corte Masculino*, *Escova*, etc., com preço.

Os serviços também podem ser criados automaticamente durante a confirmação do agendamento.

### D. Fluxo de teste do agendamento (cliente)

1. Login como **cliente**.
2. Escolha o **dia** .
3. Escolha o **horário** .
4. Selecione os **serviços** e confirme.
5. Visualize o agendamento no **dashboard do cliente**


Horários disponíveis: das **08:00** às **11:00** e das **14:00** às **18:00**, em intervalos de 30 minutos.

---

## Comandos úteis

```bash
# Verificar se o projeto está configurado corretamente
python manage.py check

# Abrir shell interativo do Django
python manage.py shell
```

---

## Solução de problemas

### `Couldn't import Django`

O ambiente virtual não está ativo ou as dependências não foram instaladas. Ative o `.venv` e rode `pip install -r requirements.txt` novamente.

### `database is locked` (SQLite)

Evite manter o projeto dentro de pastas sincronizadas (OneDrive, Google Drive). Se o erro persistir, feche outros processos que possam estar usando o banco e reinicie o `runserver`.

### Erro ao confirmar agendamento: "Nenhum profissional cadastrado"

Cadastre um profissional usando o código `STUDIO-PRO-2026` (seção **A** acima).

### Porta 8000 já em uso

Inicie em outra porta:

```bash
python manage.py runserver 8080
```

---

## Tecnologias

- [Django 6.0](https://docs.djangoproject.com/en/6.0/)
- SQLite
- HTML, CSS e JavaScript (templates Django)

---

## Licença

Projeto acadêmico — consulte o autor do repositório para detalhes de uso.
