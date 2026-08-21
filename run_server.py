"""
Launcher principal de Churn Sentinel AI.
Inicia el servidor FastAPI en http://127.0.0.1:8000 y sirve la interfaz web reactiva.
"""
import os
import sys
import webbrowser
import threading
import time

# Configurar PYTHONPATH con la raíz del proyecto y backend
project_root = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(project_root, "backend")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn


def open_browser():
    time.sleep(1.5)
    print("\n[OK] Abriendo Dashboard en: http://127.0.0.1:8000 ...\n")
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("=" * 70)
    print("   CHURN SENTINEL AI - INICIALIZADOR DE SERVIDOR INTEGRADO")
    print("   Backend (FastAPI) + Frontend (Dashboard) + Inferencia en Cascada")
    print("=" * 70)

    from backend.app.main import app

    # Iniciar hilo para abrir navegador
    threading.Thread(target=open_browser, daemon=True).start()

    # Iniciar servidor Uvicorn con recarga automática
    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir, os.path.join(project_root, "frontend")],
        log_level="info"
    )
