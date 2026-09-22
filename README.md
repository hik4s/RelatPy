# RelatPy

Automação interna para extração de relatórios do SGIND e IQOS com Playwright, execução paralela controlada, painel Streamlit, acompanhamento por `status.json`, renomeação dos arquivos e cópia para diretórios corporativos.

## Funcionalidades

- Login centralizado com credenciais armazenadas em `.env`.
- Tela de primeiro acesso no Streamlit quando o `.env` não existe.
- Extração de sete relatórios:
  - Compensação
  - Reclamações
  - Interrupções por Cliente
  - Eventos
  - Ocorrências
  - Dia Crítico
  - IQOS
- Execução paralela e sequencial configurável por relatório.
- Acompanhamento dos estados `PENDENTE`, `EXECUTANDO`, `CONCLUIDO`, `REMOVIDO`, `CANCELADO` e `ERRO`.
- Validação do arquivo local e da cópia na rede.
- Download dos arquivos pelo dashboard.
- Log em tempo real da execução atual.
- Botão para interromper somente o worker atual e seus processos-filhos.
- Botão para encerrar o servidor Streamlit com segurança.
- Splash screen e launcher compatível com PyInstaller.

## Requisitos

- Windows 10 ou Windows 11.
- Python 3.9 ou superior. Python 3.11 ou 3.12 é recomendado.
- Microsoft Edge instalado.
- Acesso autorizado aos portais internos e aos diretórios corporativos configurados.
- Conectividade com a rede corporativa.

## Estrutura do projeto

```text
RelatPy-master/
├── RelatPy.exe                  # launcher opcional empacotado
├── launcher.py                  # splash e inicialização do Streamlit
├── worker.py                    # execução isolada da automação
├── main.py                      # entrada tradicional pelo terminal
├── auth.py                      # credenciais e login Playwright
├── config.py                    # configuração dos relatórios
├── downloader.py                # orquestração dos downloads
├── requisitos.txt               # dependências Python
├── .env                         # credenciais locais, nunca versionar
├── .gitignore
├── README.md
│
├── core/
│   ├── app_control.py           # encerramento controlado do dashboard
│   ├── executor.py              # paralelismo e status
│   └── file_manager.py          # nomes, cópia e validação na rede
│
├── relatorios/
│   ├── compensacao.py
│   ├── reclamacao.py
│   ├── interrupcoes_cliente.py
│   ├── interrupcoes_evento.py
│   ├── todas_ocorrencias.py
│   ├── dia_critico.py
│   └── iqos_resultados.py
│
├── ui/
│   └── streamlit_app.py
│
├── assets/
│   └── logo.ico
│
├── downloads/                   # gerado em tempo de execução
├── logs/                        # gerado em tempo de execução
├── status/                      # JSON, PIDs e controle de encerramento
└── venv/                        # ambiente virtual local
```

## Instalação

Na raiz do projeto, crie o ambiente virtual:

```powershell
python -m venv venv
```

Ative o ambiente:

```powershell
.\venv\Scripts\Activate.ps1
```

Se a política do PowerShell bloquear a ativação, execute o Python do ambiente diretamente nos comandos seguintes.

Instale as dependências:

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requisitos.txt
```

Instale o Microsoft Edge para o Playwright:

```powershell
.\venv\Scripts\python.exe -m playwright install msedge
```

## Dependências esperadas

O arquivo `requisitos.txt` deve conter pelo menos:

```text
playwright>=1.47
python-dotenv>=1.0
streamlit>=1.49
streamlit-autorefresh>=1.0
```

Para gerar o executável do launcher, instale também:

```powershell
.\venv\Scripts\python.exe -m pip install pyinstaller
```

## Credenciais

Na primeira abertura pelo dashboard, informe o usuário e a senha na tela de primeiro acesso. O projeto criará um arquivo `.env` na raiz com o formato:

```dotenv
SITE_USUARIO="seu_usuario"
SITE_SENHA="sua_senha"
```

O arquivo `.env` é local e está ignorado pelo Git.

> Atenção: o `.env` armazena a senha em texto legível. Restrinja o acesso à pasta do projeto e nunca envie esse arquivo ao repositório, por e-mail ou por chat.

## Como executar

### Dashboard Streamlit

```powershell
.\venv\Scripts\python.exe -m streamlit run ui\streamlit_app.py
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8501
```

### Launcher gráfico

```powershell
.\venv\Scripts\pythonw.exe launcher.py
```

O launcher exibe a splash, inicia o Streamlit sem console e abre o navegador quando a porta estiver disponível.

### Execução tradicional pelo terminal

```powershell
.\venv\Scripts\python.exe main.py
```

## Fluxo da execução

```text
Dashboard
  ↓
worker.py
  ↓
main.py
  ↓
downloader.py
  ↓
executor.py + relatórios Playwright
  ↓
download local
  ↓
file_manager.py
  ↓
cópia para a rede
  ↓
status.json + worker.log
```

O dashboard inicia o `worker.py` como processo separado. Assim, atualizar ou fechar a aba não interrompe automaticamente uma extração em andamento.

## Estados dos relatórios

- `PENDENTE`: aguardando início.
- `EXECUTANDO`: relatório em processamento.
- `CONCLUIDO`: processamento concluído.
- `REMOVIDO`: exportação removida ou cancelada pelo sistema de origem.
- `CANCELADO`: execução interrompida manualmente no dashboard.
- `ERRO`: falha durante navegação, exportação, download ou processamento.

## Arquivos de execução

### `status/status.json`

Armazena o estado atual de cada relatório, incluindo:

```json
{
  "reclamacao": {
    "status": "CONCLUIDO",
    "detalhe": null,
    "arquivo_local": "downloads\\arquivo.csv",
    "arquivo_rede": "\\\\servidor\\pasta\\arquivo.csv",
    "ultima_atualizacao": "21/09/2026 14:00:00"
  }
}
```

### `status/worker.pid`

Identifica somente o processo `worker.py` atual. O botão **Parar execução** valida esse PID antes de encerrar a árvore de processos.

### `logs/worker.log`

Contém apenas a execução atual. Os logs antigos do worker são removidos quando uma nova execução começa.

### `logs/streamlit.log`

É preservado enquanto o servidor estiver aberto, pois pode estar em uso pelo launcher e pelo Streamlit.

## Interromper uma execução

Use o botão **Parar execução** no dashboard. O fluxo:

1. valida se o PID pertence ao `worker.py`;
2. encerra o worker e os processos-filhos do Playwright;
3. remove `status/worker.pid`;
4. mantém relatórios concluídos como `CONCLUIDO`;
5. altera relatórios pendentes ou em execução para `CANCELADO`;
6. libera novamente o botão de execução.

Não use comandos que encerrem todos os processos `python.exe` da máquina.

## Encerrar o RelatPy

Use o botão **Fechar RelatPy** para solicitar o encerramento controlado do servidor Streamlit. Fechar somente a aba do navegador não é garantia de encerramento do servidor nem do worker.

Se houver uma extração em andamento, o worker pode continuar em segundo plano. Use **Parar execução** antes de fechar se quiser cancelar os relatórios.

## Gerar o executável do launcher

O executável continua usando o `venv` e os arquivos externos do projeto. Gere-o com:

```powershell
.\venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name RelatPy --icon "assets\logo.ico" launcher.py
```

Sem ícone:

```powershell
.\venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name RelatPy launcher.py
```

Depois copie:

```text
dist\RelatPy.exe
```

para a raiz do projeto. Não distribua somente o executável. O launcher depende de `venv`, `ui`, `core`, `relatorios` e dos demais arquivos do projeto.

## Como testar

### Imports principais

```powershell
.\venv\Scripts\python.exe -c "from auth import tentar_login, obter_credenciais, ler_credenciais_env, salvar_credenciais; print('Imports OK')"
```

### Credenciais sem exibir valores

```powershell
.\venv\Scripts\python.exe -c "from auth import ler_credenciais_env; u, s = ler_credenciais_env(); print('Usuário:', bool(u)); print('Senha:', bool(s))"
```

### Verificar worker ativo

```powershell
Get-CimInstance Win32_Process |
Where-Object { $_.CommandLine -like "*worker.py*" } |
Select-Object ProcessId, CommandLine
```

### Limpar PID obsoleto

Use somente quando não existir processo `worker.py` ativo:

```powershell
Remove-Item status\worker.pid -ErrorAction SilentlyContinue
```

### Teste funcional sugerido

1. Abra o RelatPy.
2. Confirme que o painel carrega sem execução automática.
3. Selecione o período.
4. Clique em **Executar Relatórios**.
5. Confirme a criação de `status/worker.pid`.
6. Confirme que os sete relatórios aparecem no `status.json`.
7. Acompanhe o `worker.log` no dashboard.
8. Feche e reabra a aba, confirmando que o status permanece.
9. Teste **Parar execução** durante um relatório.
10. Inicie uma nova execução e valide a limpeza dos logs antigos.
11. Confirme os arquivos locais e as cópias na rede.

## Solução de problemas

### Botão mostra “Execução em andamento”, mas não há worker

Verifique:

```powershell
Get-Content status\worker.pid
```

Depois consulte o PID. Se não pertencer ao `worker.py`, remova o arquivo PID e atualize o dashboard.

### Log vazio

O worker deve ser iniciado com `-u` e com:

```text
PYTHONUNBUFFERED=1
```

O dashboard atual já utiliza essas opções.

### `EOFError` ao pedir usuário

O worker não possui console interativo. Configure as credenciais pela tela de primeiro acesso e confirme que o `.env` contém `SITE_USUARIO` e `SITE_SENHA`.

### ImportError em `auth.py`

Confirme que o arquivo contém simultaneamente:

- `tentar_login`
- `fazer_login`
- `obter_credenciais`
- `ler_credenciais_env`
- `salvar_credenciais`

Depois feche os processos antigos e remova as pastas `__pycache__`.

### Navegador abre, mas o servidor não responde

Consulte:

```text
logs\streamlit.log
```

### Falha ao copiar para a rede

Verifique:

- conexão com a rede corporativa;
- permissão de escrita;
- caminho configurado em `core/file_manager.py`;
- nome final calculado para o período;
- disponibilidade do compartilhamento.

## Cuidados de segurança

- Nunca versione o `.env`.
- Não grave credenciais em logs ou no `status.json`.
- Restrinja as permissões da pasta do projeto.
- Mantenha o Streamlit limitado a `127.0.0.1`.
- Não use `taskkill /IM python.exe`.
- Atualize regularmente as dependências em ambiente de teste antes de produção.
- Interromper durante uma cópia pode deixar arquivo parcial no compartilhamento. Uma evolução recomendada é copiar para `.tmp` e renomear após conclusão.
- Valide alterações em um período pequeno antes de executar todos os relatórios.

## Versionamento

Sugestão de fluxo:

```powershell
git status
git add .gitignore README.md
git commit -m "docs: atualizar documentação e arquivos ignorados"
git push hik4s master
```

## Licença e uso

Projeto destinado a uso interno e autorizado. Revise as políticas corporativas antes de distribuir o código, o executável, caminhos de rede ou qualquer configuração do ambiente.
