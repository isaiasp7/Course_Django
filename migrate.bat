@echo off
cd /d "%~dp0AgentamentoSystem"
"%~dp0.venv\Scripts\python.exe" manage.py migrate %*
if errorlevel 1 (
    echo.
    echo Migrate falhou. Use sempre este script ou ative o .venv antes.
    pause
    exit /b 1
)
echo.
echo Migrate concluido com sucesso.
pause
