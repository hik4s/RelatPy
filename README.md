<<<<<<< HEAD
# Automação de Extração de Relatórios

Script em Python que automatiza o login e o download de múltiplos relatórios de um sistema interno via navegador, eliminando um processo antes feito manualmente, um relatório de cada vez.

## O problema

O processo original exigia acessar manualmente 7 páginas diferentes do mesmo sistema, preencher filtros de data em formatos distintos (`dd/mm/yyyy` e `dd/mm/yyyy hh:mm:ss`), aguardar o processamento de cada exportação e baixar os arquivos um a um — um processo repetitivo e sujeito a erro humano.

## A solução

Um script que:
- Faz login uma única vez;
- Abre uma aba por relatório e processa todos **em paralelo** (não sequencialmente);
- Preenche automaticamente os filtros de data no formato correto de cada página;
- Aguarda o processamento de cada exportação e baixa o arquivo certo, evitando conflito entre downloads simultâneos;
- Roda com um duplo clique, sem depender de o usuário ter Python ou dependências pré-instaladas.

## Arquitetura

```
main.py           → ponto de entrada; captura o período e dispara o processo
downloader.py     → orquestra as 7 abas em paralelo (asyncio)
auth.py           → login único, compartilhado entre todas as abas
config.py         → lista de relatórios, cada um apontando para seu módulo
relatorios/
  ├── _template.py     → esqueleto para adicionar um novo relatório
  └── <nome>.py         → lógica específica de cada relatório (um módulo por página)
rodar.bat         → verifica/instala dependências e Python, e executa o projeto
requisitos.txt    → dependências do projeto
```

Cada relatório é um módulo independente com uma função de entrada padrão (`processar`), o que torna simples adicionar um novo relatório sem alterar a lógica central — só criar o módulo e registrá-lo em `config.py`.

## Principais decisões técnicas

**Playwright (API assíncrona) em vez de Selenium.** Permite abrir e processar as 7 abas simultaneamente com `asyncio.gather`, além de lidar com downloads e esperas de forma mais confiável que `time.sleep` fixo.

**Design orientado a configuração.** Em vez de se hardcode um fluxo por página, cada relatório é descrito como um dicionário em `config.py` e delega a lógica específica a um módulo próprio — o núcleo do sistema (`downloader.py`) não precisa saber os detalhes de nenhum relatório específico.

**Módulo de execução portátil (`.bat`).** Detecta se o Python está instalado (instalando via `winget` automaticamente se não estiver), cria um ambiente virtual isolado, instala as dependências e garante o navegador do Playwright — tudo isso sem intervenção manual em uma máquina nova.

## Desafio técnico: sessão perdida entre abas

Um problema não-óbvio surgiu ao rodar os relatórios em paralelo: cada aba nova pedia login novamente, mesmo dentro do mesmo contexto do navegador (que já compartilha cookies automaticamente).

**Causa:** o sistema guarda o token de autenticação no `sessionStorage`, que — diferente de cookies e `localStorage` — é isolado por aba, mesmo com a mesma sessão de navegador.

**Solução:** após o login, o script captura o conteúdo do `sessionStorage` e registra um *init script* no contexto do navegador (`context.add_init_script`), que restaura esse estado em toda aba nova **antes** de qualquer script da própria aplicação rodar — eliminando a necessidade de logar em cada aba individualmente.

## Segurança

- Credenciais ficam em um arquivo `.env`, nunca commitado (`.gitignore` cobre `.env`, sessões salvas e arquivos baixados).
- O script valida a presença do `.env` antes de rodar, evitando falhas confusas por variável ausente.

## Tecnologias

Python 3 · Playwright (async) · python-dotenv · asyncio · Git

## O que eu aprenderia/melhoraria a seguir

- Substituir os `wait_for_timeout` fixos por esperas mais robustas baseadas em eventos da página.
- Adicionar testes automatizados para os módulos de relatório.
=======
# Automação de Extração de Relatórios

Script em Python que automatiza o login e o download de múltiplos relatórios de um sistema interno via navegador, eliminando um processo antes feito manualmente, um relatório de cada vez.

## O problema

O processo original exigia acessar manualmente 7 páginas diferentes do mesmo sistema, preencher filtros de data em formatos distintos (`dd/mm/yyyy` e `dd/mm/yyyy hh:mm:ss`), aguardar o processamento de cada exportação e baixar os arquivos um a um — um processo repetitivo e sujeito a erro humano.

## A solução

Um script que:
- Faz login uma única vez;
- Abre uma aba por relatório e processa todos **em paralelo** (não sequencialmente);
- Preenche automaticamente os filtros de data no formato correto de cada página;
- Aguarda o processamento de cada exportação e baixa o arquivo certo, evitando conflito entre downloads simultâneos;
- Roda com um duplo clique, sem depender de o usuário ter Python ou dependências pré-instaladas.

## Arquitetura

```
main.py           → ponto de entrada; captura o período e dispara o processo
downloader.py     → orquestra as 7 abas em paralelo (asyncio)
auth.py           → login único, compartilhado entre todas as abas
config.py         → lista de relatórios, cada um apontando para seu módulo
relatorios/
  ├── _template.py     → esqueleto para adicionar um novo relatório
  └── <nome>.py         → lógica específica de cada relatório (um módulo por página)
rodar.bat         → verifica/instala dependências e Python, e executa o projeto
requisitos.txt    → dependências do projeto
```

Cada relatório é um módulo independente com uma função de entrada padrão (`processar`), o que torna simples adicionar um novo relatório sem alterar a lógica central — só criar o módulo e registrá-lo em `config.py`.

## Principais decisões técnicas

**Playwright (API assíncrona) em vez de Selenium.** Permite abrir e processar as 7 abas simultaneamente com `asyncio.gather`, além de lidar com downloads e esperas de forma mais confiável que `time.sleep` fixo.

**Design orientado a configuração.** Em vez de se hardcode um fluxo por página, cada relatório é descrito como um dicionário em `config.py` e delega a lógica específica a um módulo próprio — o núcleo do sistema (`downloader.py`) não precisa saber os detalhes de nenhum relatório específico.

**Módulo de execução portátil (`.bat`).** Detecta se o Python está instalado (instalando via `winget` automaticamente se não estiver), cria um ambiente virtual isolado, instala as dependências e garante o navegador do Playwright — tudo isso sem intervenção manual em uma máquina nova.

## Desafio técnico: sessão perdida entre abas

Um problema não-óbvio surgiu ao rodar os relatórios em paralelo: cada aba nova pedia login novamente, mesmo dentro do mesmo contexto do navegador (que já compartilha cookies automaticamente).

**Causa:** o sistema guarda o token de autenticação no `sessionStorage`, que — diferente de cookies e `localStorage` — é isolado por aba, mesmo com a mesma sessão de navegador.

**Solução:** após o login, o script captura o conteúdo do `sessionStorage` e registra um *init script* no contexto do navegador (`context.add_init_script`), que restaura esse estado em toda aba nova **antes** de qualquer script da própria aplicação rodar — eliminando a necessidade de logar em cada aba individualmente.

## Segurança

- Credenciais ficam em um arquivo `.env`, nunca commitado (`.gitignore` cobre `.env`, sessões salvas e arquivos baixados).
- O script valida a presença do `.env` antes de rodar, evitando falhas confusas por variável ausente.

## Tecnologias

Python 3 · Playwright (async) · python-dotenv · asyncio · Git

## O que eu aprenderia/melhoraria a seguir

- Substituir os `wait_for_timeout` fixos por esperas mais robustas baseadas em eventos da página.
- Adicionar testes automatizados para os módulos de relatório.
>>>>>>> e2dd4c4c1918cbb48850cc3e1a4aa97cecab32ba
- Migrar a configuração de relatórios para um arquivo YAML/JSON externo, facilitando ajustes sem tocar em código Python.