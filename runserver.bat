@echo off
cd /d "%~dp0AgentamentoSystem"
"%~dp0.venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
