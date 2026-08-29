"""Caminhos e configuração compartilhada do backend.

Coloca a raiz do projeto (``tech-challenge-fase1/``) e a pasta ``scripts/``
no ``sys.path`` para que o backend reaproveite ``src/pipeline.py`` e
``scripts/generate_report_pdf.py`` sem duplicar código.
"""

import sys
from pathlib import Path

# backend/app/core.py -> backend/app -> backend -> tech-challenge-fase1
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
REPORTS_DIR = PROJECT_DIR / "reports"
SCRIPTS_DIR = PROJECT_DIR / "scripts"

DEFAULT_DATASET = DATA_DIR / "data.csv"

for path in (PROJECT_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# CORS: porta padrão do `ng serve` do Angular
ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://localhost:58813",
    "http://127.0.0.1:4200",
]
