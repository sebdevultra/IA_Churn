"""
Configuración de rutas de Pytest para ai_pipeline/test/
Asegura que la raíz del proyecto esté en sys.path.
"""

import os
import sys

# La raíz del proyecto está 2 niveles arriba de ai_pipeline/test/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
