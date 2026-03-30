@echo off
setlocal

set "MAIN=src\main\python\org\example\main.py"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "%MAIN%"
    exit /b %errorlevel%
)

if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" "%MAIN%"
    exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo No se encontro Python en el sistema.
    echo Instala Python 3.10+ o crea un entorno .venv en esta carpeta.
    exit /b 1
)

python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Se detecto el alias de Python, pero no hay un interprete funcional instalado.
    echo Instala Python 3.10+ o crea un entorno .venv en esta carpeta.
    exit /b 1
)

python "%MAIN%"
exit /b %errorlevel%
