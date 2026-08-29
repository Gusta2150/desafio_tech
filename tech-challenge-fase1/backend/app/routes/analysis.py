"""POST /api/analysis — roda o pipeline completo (equivalente ao notebook inteiro)."""

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core import DEFAULT_DATASET
from app.schemas import AnalysisResponse
from app.store import analyses
from src.pipeline import IncompatibleDatasetError, run_full_analysis

router = APIRouter(tags=["analysis"])


@router.post("/analysis", response_model=AnalysisResponse)
async def create_analysis(file: UploadFile | None = File(default=None)):
    """Recebe um CSV (ou usa o dataset padrão do projeto) e roda validação,
    EDA, treino, avaliação e explicabilidade — tudo que o notebook faz."""
    if file is not None:
        file_bytes = await file.read()
    else:
        if not DEFAULT_DATASET.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum arquivo enviado e dataset padrão não encontrado em {DEFAULT_DATASET}.",
            )
        file_bytes = DEFAULT_DATASET.read_bytes()

    try:
        result = run_full_analysis(file_bytes)
    except IncompatibleDatasetError as error:
        raise HTTPException(status_code=422, detail=error.details) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    analysis_id = str(uuid.uuid4())
    analyses[analysis_id] = result

    return {
        "analysis_id": analysis_id,
        "identificacao_csv": result.identificacao_csv,
        "eda": result.eda,
        "models_comparison": (
            result.results_df.round(4).to_dict(orient="records") if result.results_df is not None else []
        ),
        "best_model": result.best_name,
        "evaluation": result.evaluation,
        "explainability": result.explainability,
        "feature_names": result.X_columns,
        "trainable": result.trainable,
        "trainable_issue": result.trainable_issue,
    }
