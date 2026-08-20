@echo off
TITLE ChurnGuard AI - Suite de Pruebas Automatizadas
COLOR 0A

echo ================================================================
echo    CHURNGUARD AI - EJECUTOR DE PRUEBAS AUTOMATIZADAS (PYTEST)
echo ================================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta primero 'run_local.bat'.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [INFO] Ejecutando 27 pruebas con reporte de cobertura...
echo.
pytest -v --cov=backend.app backend/tests

echo.
echo ================================================================
echo Pruebas finalizadas.
echo ================================================================
pause
