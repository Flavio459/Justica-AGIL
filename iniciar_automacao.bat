@echo off
echo ===================================================
echo   INICIANDO MODO AUTOMCAO SEGURA - PROCON AGIL
echo   (Versao Isolada - Nao interfere no seu Chrome)
echo ===================================================
echo.

echo 1. Criando perfil temporario para automacao...
if not exist "c:\temp_chrome_debug" mkdir "c:\temp_chrome_debug"

echo.
echo 2. Abrindo Chrome Especial (Isolado)...
echo    - Faca o LOGIN no Gov.br NESTE NOVO NAVEGADOR
echo    - Ele vai abrir "zerado", isso e normal e necessario.
echo.

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="c:\temp_chrome_debug" --no-first-run --no-default-browser-check

echo 3. Aguardando voce fazer login...
echo.
echo    QUANDO TERMINAR O LOGIN, APERTE QUALQUER TECLA AQUI.
echo.
pause

echo 4. Iniciando o Robô...
cd backend
python run_real_claim.py
pause
