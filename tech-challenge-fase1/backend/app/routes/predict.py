"""POST /api/predict — usa o modelo já treinado de uma análise para prever novas amostras."""

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.schemas import PredictRequest, PredictResponse
from app.store import analyses
from src.pipeline import IncompatibleDatasetError, predict_samples

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    analysis = analyses.get(request.analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="analysis_id não encontrado. Rode POST /api/analysis primeiro.",
        )

    if not analysis.trainable or analysis.best_model is None:
        raise HTTPException(
            status_code=422,
            detail={
                "status": "Modelo não disponível",
                "mensagem": (
                    "Esta análise não treinou um modelo (o arquivo tinha poucas amostras). "
                    "Rode uma análise com um dataset maior — por exemplo, o dataset padrão do "
                    "projeto — e use a aba \"Prever amostra\" a partir dela."
                ),
            },
        )

    amostras = pd.DataFrame(request.samples)
    try:
        result_df = predict_samples(
            analysis.best_model, analysis.X_columns, amostras, request.limiar
        )
    except IncompatibleDatasetError as error:
        raise HTTPException(status_code=422, detail=error.details) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return {"predictions": result_df.to_dict(orient="records")}
