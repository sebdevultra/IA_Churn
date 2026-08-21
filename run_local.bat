@echo off
TITLE Churn Sentinel AI - Monitor de Sentimiento y Riesgo
COLOR 0B

echo ================================================================
echo    CHURN SENTINEL AI - INICIALIZADOR DE SERVIDOR INTEGRADO
echo ================================================================
echo.

:: 1. Verificar y configurar el archivo .env si no existe
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo [INFO] Creando archivo backend\.env desde .env.example...
        copy backend\.env.example backend\.env >nul
    )
)

:: 2. Liberar puerto 8000 si quedo ocupado
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Liberando puerto 8000 ocupado por PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

:: 3. Ejecutar launcher python
python run_server.py

pause
