import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para encontrar logica_negocio
path_root = Path(__file__).resolve().parent.parent
sys.path.append(str(path_root))

from logica_negocio.main import app

# Vercel espera una variable llamada 'app'
# Pero FastAPI es un objeto ASGI, así que simplemente lo exportamos
# (Vercel lo manejará automáticamente con el builder de python)
