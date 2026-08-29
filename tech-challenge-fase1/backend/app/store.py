"""Estado em memória das análises já treinadas.

Simples e suficiente para uma demo/vídeo com um único processo. Cada upload
bem-sucedido em ``POST /api/analysis`` fica guardado aqui, indexado por
``analysis_id``, para que ``/api/predict`` e ``/api/report/pdf`` consigam
reutilizar o mesmo modelo treinado sem re-treinar a cada chamada.
"""

import app.core  # noqa: F401  (import por efeito colateral: ajusta o sys.path)
from src.pipeline import TrainedAnalysis

analyses: dict[str, TrainedAnalysis] = {}
