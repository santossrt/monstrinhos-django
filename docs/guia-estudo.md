# Guia de estudo — Monstrinhos

Esta adaptação usa o percurso da apostila “Construindo o Fliperama Django”, com criaturas colecionáveis no lugar dos jogos. Comece executando os passos do [README](../README.md).

## 1. Do endereço ao HTML

Siga uma visita à coleção: `config/urls.py` encaminha a URL para `monstrinhos/urls.py`; a view em `views.py` consulta o model e chama `render()`; o template gera o HTML entregue ao navegador. Abra também os detalhes de um monstrinho para observar uma rota com parâmetro.

## 2. Templates e aparência

Leia `templates/monstrinhos/base.html` e encontre os blocos substituídos pelas outras páginas. A folha `static/monstrinhos/style.css` define a aparência responsiva. As ilustrações são locais, por isso a interface não depende de um serviço de imagens.

## 3. Componentes reutilizáveis

Localize os `{% include %}` de `_menu.html`, `_card.html` e `_criatura.html`. Um cartão pode aparecer para diferentes monstrinhos sem repetir toda sua estrutura. A criatura varia conforme o elemento.

## 4. Estados com durações diferentes

| Informação | Onde fica | O que acontece ao atualizar a página |
| --- | --- | --- |
| Nome, elemento, nível e alimentações | SQLite | Permanecem salvos |
| Visitas à coleção | Sessão Django | Continuam na mesma sessão |
| Pontos e tempo de uma batalha | Memória do JavaScript | A partida reinicia |
| Melhor pontuação por monstrinho | `localStorage` do navegador | Permanece quando esse armazenamento está disponível |

Experimente alimentar uma criatura e atualizar os detalhes. Depois, faça uma batalha e atualize novamente. Compare os dados que permanecem.

## 5. Rotas e navegação

Os templates usam `{% url 'monstrinhos:detalhe' monstrinho.pk %}` para gerar links. Abra a busca e os filtros e observe os parâmetros GET na barra de endereço. Consultas não alimentam os monstrinhos.

## 6. Dois tipos de evento

**Alimentar:** o formulário inclui `{% csrf_token %}` e envia POST. A view exige esse método, atualiza o banco e redireciona para os detalhes. O nível fica limitado a 50. A atualização usa expressões do banco para evitar perder incrementos concorrentes.

**Batalha:** o navegador inicia uma partida de 10 segundos e conta interações no alvo. O JavaScript verifica o prazo usando um relógio monotônico. Esse evento não altera o banco e não concede níveis. O recorde é local, sem caráter competitivo entre usuários.

## 7. Formulários e validação

Leia `forms.py` junto de `models.py`. Cadastre um nome com espaços nas extremidades e depois tente repeti-lo em maiúsculas. Teste níveis 0 e 51. Os dados inválidos devem manter o formulário preenchido com mensagens de erro, sem criar uma criatura.

A interface ajuda a preencher; a validação no servidor decide se o cadastro é aceito. As restrições de banco reforçam os limites e a unicidade. O campo interno de nome normalizado permite tratar letras acentuadas de forma consistente no SQLite.

## Executar as verificações

```bash
python manage.py test
node --test tests/batalha.test.cjs
```

O primeiro comando usa Django; o segundo requer Node.js e testa o comportamento do minijogo sem serviços externos. Consulte o README para os demais passos de execução.
