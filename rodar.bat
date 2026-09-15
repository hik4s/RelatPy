::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFBNdRwWRAE+1EbsQ5+n//Na1p0EcQNImNobY1dQ=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSjk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSTk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+IeA==
::cxY6rQJ7JhzQF1fEqQJhZksaHErRXA==
::ZQ05rAF9IBncCkqN+0xwdVsFAlTMbCXpZg==
::ZQ05rAF9IAHYFVzEqQICLRdVWDSbXA==
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWHGN/0MjSA==
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATE3Es7KQg0
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJHiR4E09KRhVQziwOWe7EoUFpu3j6oo=
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal

rem %~dp0 = pasta onde este .bat/.exe está, nao importa o computador/caminho
cd /d "%~dp0"

rem =====================================================
rem  AJUSTE AQUI: nome exato do .exe gerado pelo Bat To Exe
rem  Converter (o mesmo nome que voce escolheu no "Save as").
rem =====================================================
set "NOME_EXE=RelatPy.exe"
set "NOME_ATALHO=RelatPy"

rem --- Cria o atalho na Area de Trabalho, so na primeira vez ---
if not exist "%~dp0.atalho_criado" (
    echo Criando atalho na Area de Trabalho...

    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$ws = New-Object -ComObject WScript.Shell;" ^
        "$lnk = $ws.CreateShortcut('%USERPROFILE%\Desktop\%NOME_ATALHO%.lnk');" ^
        "$lnk.TargetPath = '%~dp0%NOME_EXE%';" ^
        "$lnk.WorkingDirectory = '%~dp0';" ^
        "$lnk.IconLocation = '%~dp0%NOME_EXE%';" ^
        "$lnk.Save()"

    if not errorlevel 1 (
        echo. > "%~dp0.atalho_criado"
        echo Atalho criado na Area de Trabalho.
    ) else (
        echo [AVISO] Nao foi possivel criar o atalho automaticamente.
    )
)

rem --- Verifica se o Python esta instalado e acessivel ---
where python >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado. Executando instalador automatico...
    echo.
    call :instalar_python

    rem Tenta recarregar o PATH nesta mesma janela, sem precisar
    rem fechar e abrir de novo (o winget atualiza o registro, mas
    rem o cmd atual ainda esta com o PATH antigo em memoria).
    for /f "skip=2 tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SysPath=%%B"
    for /f "skip=2 tokens=2,*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "UserPath=%%B"
    set "PATH=%SysPath%;%UserPath%;%PATH%"

    where python >nul 2>nul
    if errorlevel 1 (
        echo.
        echo [ERRO] O Python foi instalado, mas ainda nao foi possivel
        echo detecta-lo nesta janela. Feche esta janela, abra o rodar
        echo novamente e tente de novo.
        pause
        exit /b 1
    )

    echo Python detectado com sucesso apos a instalacao.
)

rem --- Cria o ambiente virtual na primeira execucao ---
if not exist "venv\" (
    echo Criando ambiente virtual pela primeira vez...
    python -m venv venv
)

call venv\Scripts\activate.bat

rem --- Instala/atualiza as dependencias do projeto ---
echo Verificando dependencias...
pip install -r requisitos.txt --quiet

rem --- Garante que o navegador Edge do Playwright esta instalado ---
python -m playwright install msedge

rem --- Avisa (sem bloquear) se o .env ainda nao existe ---
rem O proprio script Python ja sabe pedir as credenciais no console
rem e salvar o .env sozinho quando ele nao existir - entao aqui so
rem avisamos, sem impedir a execucao.
if not exist ".env" (
    echo [INFO] Arquivo .env nao encontrado. O script vai pedir suas
    echo credenciais no console e salvar automaticamente para a
    echo proxima execucao.
    echo.
)

echo.
echo Iniciando o script...
echo.

python main.py

pause
exit /b 0


rem =====================================================
rem  Sub-rotina: instala o Python via winget se preciso
rem =====================================================
:instalar_python
where winget >nul 2>nul
if errorlevel 1 (
    echo [ERRO] O winget nao foi encontrado neste computador.
    echo Isso costuma acontecer em versoes mais antigas do Windows 10.
    echo Baixe o Python manualmente em: https://www.python.org/downloads/
    echo IMPORTANTE: marque a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

echo Instalando Python via winget, aguarde...
echo (pode abrir uma janela de confirmacao do Windows, aceite para continuar)
echo.

winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements

if errorlevel 1 (
    echo.
    echo [ERRO] A instalacao via winget falhou ou foi cancelada.
    echo Tente baixar manualmente em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Python instalado com sucesso!
goto :eof