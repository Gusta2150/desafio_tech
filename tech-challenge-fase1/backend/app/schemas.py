"""Modelos Pydantic de request/response da API.

As seções vindas diretamente do `src/pipeline.py` (eda, evaluation,
explainability, identificacao_csv) têm estrutura dinâmica (nomes de
colunas do dataset como chaves), então ficam tipadas como `dict`/`Any` —
o contrato fixo (nomes de campos e tipos) está documentado em
`src/pipeline.py` e no `frontend/src/app/core/models/analysis.model.ts`.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ModelComparisonRow(BaseModel):
    modelo: str
    accuracy: float
    recall_maligno: float
    f1_maligno: float
    roc_auc: float


class AnalysisResponse(BaseModel):
    analysis_id: str
    identificacao_csv: dict[str, Any]
    eda: dict[str, Any]
    models_comparison: list[ModelComparisonRow]
    best_model: str | None
    evaluation: dict[str, Any]
    explainability: dict[str, Any]
    feature_names: list[str]
    trainable: bool
    trainable_issue: dict[str, Any] | None = None


class PredictRequest(BaseModel):
    analysis_id: str
    samples: list[dict[str, float]] = Field(..., min_length=1)
    limiar: float = 0.50


class PredictionResult(BaseModel):
    probabilidade_malignidade: float
    limiar: float
    orientacao: str
    aviso: str


class PredictResponse(BaseModel):
    predictions: list[PredictionResult]


class ErrorDetail(BaseModel):
    status: str
    mensagem: str
    dominio_identificado: str | None = None
    campos_ausentes: list[str] | None = None
    colunas_ausentes: list[str] | None = None
