# Monstrinhos colecionáveis

Uma coleção de pequenas criaturas feita com **Python e Django**, inspirada nos conceitos da apostila **“Construindo o Fliperama Django”** e adaptada para o tema Monstrinhos. Cadastre seus companheiros, escolha um elemento, alimente-os e entre em uma batalha de cliques.

## O que o projeto faz

- Exibe a coleção em cartões ilustrados e uma página de detalhes para cada monstrinho.
- Cadastra monstrinhos com **nome único**, elemento **fogo, água ou planta** e **nível de 1 a 50**.
- Recusa nomes repetidos mesmo com diferenças de maiúsculas/minúsculas, inclusive em nomes acentuados. Remove espaços excedentes antes de salvar.
- Alimenta por uma requisição **POST** protegida por CSRF. Cada alimentação é registrada no banco e aumenta o nível em 1, até o limite de 50. No nível máximo, o monstrinho continua recebendo alimentos sem ultrapassar 50.
- Oferece uma **batalha de cliques de 10 segundos** em JavaScript, com recorde por monstrinho salvo neste navegador.
- Permite buscar por nome e filtrar a coleção por elemento.
- Conta as visitas à coleção usando a sessão do Django.
- Inclui painel administrativo e um comando opcional para criar uma coleção de exemplo.

## Tecnologias

- [Python](https://www.python.org/downloads/) **3.10 a 3.14** (verificado localmente com Python 3.13).
- [Django](https://www.djangoproject.com/) **5.2.19 LTS**, fixado em `requirements.txt`.
- SQLite, com banco local criado pelas migrações.
- HTML, CSS, JavaScript e ilustrações SVG locais, sem serviços externos necessários para executar a aplicação.

## Como executar

Pré-requisitos: Python e Git instalados. Confira `python --version` e `git --version`. Em sistemas que usam `python3`, substitua `python` por `python3` ao criar o ambiente virtual. No Windows, você também pode usar `py` se esse for o comando disponível.

### 1. Baixe o código

```bash
git clone https://github.com/santossrt/monstrinhos-django.git
cd monstrinhos-django
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

Ative no **Windows — PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

Ou no **Windows — Prompt de Comando**:

```bat
.venv\Scripts\activate.bat
```

Ou no **Linux/macOS**:

```bash
source .venv/bin/activate
```

Se o PowerShell bloquear a ativação, você pode executar todos os comandos abaixo trocando `python` por `.\.venv\Scripts\python.exe`, sem alterar a política do sistema. A ativação só serve para selecionar o Python do ambiente.

### 3. Instale as dependências e prepare o banco

```bash
python -m pip install -r requirements.txt
python manage.py migrate
```

As migrações já estão incluídas no repositório; não é necessário executar `makemigrations` para começar.

### 4. Crie a coleção de exemplo (opcional)

```bash
python manage.py popular_monstrinhos
```

O comando pode ser repetido sem duplicar os monstrinhos nem redefinir seus níveis. Se preferir começar do zero, pule esta etapa e use a página **Novo monstrinho**.

### 5. Inicie o servidor

```bash
python manage.py runserver
```

Abra **http://127.0.0.1:8000/**. Para desligar, pressione **Ctrl+C** no terminal. Os cadastros e as alimentações permanecem no arquivo local `db.sqlite3`.

### Painel administrativo (opcional)

Em outro terminal com o ambiente virtual ativado, crie seu próprio usuário:

```bash
python manage.py createsuperuser
```

Depois, acesse **http://127.0.0.1:8000/admin/**. Não há senha ou usuário administrativo predefinido.

## Como usar

1. Abra a coleção e selecione **Novo monstrinho**.
2. Informe um nome, selecione fogo, água ou planta e escolha um nível entre 1 e 50.
3. Abra os detalhes e pressione **Alimentar**. O contador e o nível são salvos no servidor.
4. Inicie a batalha e clique no alvo durante 10 segundos. O botão também funciona com o teclado quando está em foco.
5. Use a busca e os filtros para encontrar seus companheiros.

A coleção é compartilhada por quem usa esta instalação local; o projeto não implementa contas individuais de colecionador. A pontuação da batalha fica no navegador, não aumenta o nível e não é enviada ao banco. O recorde depende do armazenamento local disponível. A contagem de visitas pertence à sessão de cada navegador.

## Relação com a apostila

| Base tecnológica | Aplicação neste projeto |
| --- | --- |
| Renderização de HTML | Views com `render()` para coleção, detalhes e cadastro |
| Templates e estilização | Herança de `base.html`, folhas de estilo e imagens SVG |
| Componentes | `_menu.html`, `_card.html` e `_criatura.html` reutilizados com `{% include %}` |
| Estados | Monstrinhos e alimentações no SQLite; visitas na sessão; partida em JavaScript e recorde no `localStorage` |
| Roteamento e navegação | Rotas nomeadas, parâmetros de identificação e links com `{% url %}` |
| Eventos | Alimentar via POST no servidor e batalha de cliques no navegador |
| Formulários e validação | `MonstrinhoForm`, validação do model e restrições no banco |

O item `Jogo` do exemplo foi substituído por `Monstrinho`; gênero virou elemento; a ação de dar estrelas virou alimentar; o treino de cliques virou batalha. A faixa de nível de 1 a 50 e os elementos seguem o tema proposto.

## Rotas

| Método | Endereço | Finalidade | Nome |
| --- | --- | --- | --- |
| GET | `/` | Coleção, busca `?q=nome` e filtro `?elemento=fogo` | `monstrinhos:home` |
| GET / POST | `/novo/` | Formulário e cadastro validado | `monstrinhos:cadastrar` |
| GET | `/monstrinho/<id>/` | Detalhes e batalha no navegador | `monstrinhos:detalhe` |
| POST | `/monstrinho/<id>/alimentar/` | Alimentação e evolução de nível | `monstrinhos:alimentar` |
| GET / POST | `/admin/` | Administração autenticada | Admin do Django |

Internamente, o valor de água é `agua`, sem acento; a interface mostra **Água**. A rota de alimentação recusa GET com HTTP 405 e exige token CSRF em POST.

## Estrutura do projeto

```text
monstrinhos-django/
├── manage.py
├── requirements.txt
├── README.md
├── config/                         # Configurações, URLs principais, ASGI e WSGI
├── monstrinhos/
│   ├── models.py                   # Monstrinho e restrições dos dados
│   ├── forms.py                    # ModelForm e mensagens de validação
│   ├── views.py                    # Coleção, detalhes, cadastro e alimentação
│   ├── urls.py                     # Rotas nomeadas do app
│   ├── admin.py                    # Administração da coleção
│   ├── tests.py                    # Testes das regras e fluxos Django
│   ├── migrations/                 # Criação do esquema SQLite
│   ├── management/commands/
│   │   └── popular_monstrinhos.py  # Coleção demonstrativa idempotente
│   ├── templates/monstrinhos/      # Páginas e componentes HTML
│   └── static/monstrinhos/         # CSS, JavaScript e ilustrações locais
├── tests/batalha.test.cjs           # Testes do minijogo com Node.js
├── docs/guia-estudo.md              # Percurso para entender o código
└── .github/workflows/tests.yml     # Verificação automatizada no GitHub
```

## Como verificar o projeto

Com o ambiente virtual ativado:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Os testes Django cobrem validação, unicidade de nomes, limites de nível, filtros, cadastro, sessão, alimentação por POST, CSRF e coleção demonstrativa.

Para testar também a batalha, instale [Node.js](https://nodejs.org/) **20 ou superior** e execute:

```bash
node --test tests/batalha.test.cjs
```

Node.js é opcional para executar o site; só é usado nos testes automatizados do JavaScript. O GitHub Actions executa as verificações em cada push e pull request.

## Desenvolvimento e configuração

As configurações padrão atendem à execução local, com idioma `pt-br`, fuso `America/Sao_Paulo` e `DEBUG` ativo. O servidor `runserver` é de desenvolvimento. Publicar este código no GitHub disponibiliza o projeto para baixar e executar; isso não hospeda o servidor Django.

O banco, o ambiente virtual, ferramentas locais, caches e arquivos `.env` são ignorados pelo Git. Não envie credenciais nem seu banco de uso para o repositório.

Para estudar as partes do projeto, veja o [guia de estudo](docs/guia-estudo.md). O projeto foi entregue em uma versão integrada; não depende de tags por capítulo.

## Licença

Código e ilustrações originais deste projeto sob a licença [MIT](LICENSE). A apostila e o README de exemplo são referências didáticas e não estão redistribuídos neste repositório.
