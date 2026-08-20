@echo off
TITLE ChurnGuard AI - Servidor Local
COLOR 0B

echo ================================================================
echo    CHURNGUARD AI - INICIADOR DE SERVIDOR LOCAL
echo ================================================================
echo.

:: 1. Verificar y configurar el archivo .env con SQLite por defecto para local
if not exist ".env" (
    echo [INFO] Creando archivo de configuracion .env desde .env.example...
    copy .env.example .env >nul
    echo [OK] Archivo .env configurado.
)

:: 2. Liberar puerto 8000 si quedó ocupado por una instancia previa
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Liberando puerto 8000 ocupado por proceso PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

:: 3. Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Entorno virtual no detectado. Creando 'venv'...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual. Verifica que Python este instalado.
        pause
        exit /b 1
    )
    echo [INFO] Instalando dependencias de requirements.txt...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Error al instalar dependencias.
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate.bat
)

echo.
echo ================================================================
echo [OK] Entorno virtual activo.
echo [OK] Base de datos SQLite lista para pruebas locales.
echo [OK] Abriendo navegador en: http://localhost:8000
echo.
echo Para detener el servidor presiona Ctrl + C en esta ventana.
echo ================================================================
echo.

:: 4. Abrir automáticamente el navegador tras 2 segundos en segundo plano
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: 5. Iniciar el servidor FastAPI con Uvicorn
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

pause
