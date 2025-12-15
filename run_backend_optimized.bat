@echo off
echo ===================================================
echo   JUSTIÇA ÁGIL - MODO ALTO DESEMPENHO (BACKEND)
1echo   (Hot Reload: DESATIVADO)
echo ===================================================
echo.

cd backend
if not exist ".venv" (
    echo [ERROR] Virtualenv nao encontrado!
    pause
    exit /b
)

echo [INFO] Ativando ambiente virtual...
call .\.venv\Scripts\activate

echo [INFO] Iniciando servidor API (Uvicorn Production Mode)...
echo [INFO] Acesse http://localhost:8000/docs para testar
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --no-access-log

pause
