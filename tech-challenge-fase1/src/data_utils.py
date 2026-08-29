"""Funções auxiliares de carregamento e pré-processamento de dados."""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_raw_data(filename: str = "data.csv") -> pd.DataFrame:
    """Carrega o dataset bruto a partir da pasta data/."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em {path}. Veja data/README.md para "
            "instruções de download."
        )
    return pd.read_csv(path)
