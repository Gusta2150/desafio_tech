"""API web do Tech Challenge Fase 1 — apoio ao diagnóstico de câncer de mama.

Reaproveita o pipeline já validado em ``../src/pipeline.py`` (mesma lógica do
notebook ``01_eda.ipynb``) para servir uma aplicação web (frontend Angular)
que faz upload de um CSV e visualiza validação, EDA, modelagem, avaliação,
explicabilidade e previsão — o mesmo fluxo do notebook, ponta a ponta.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import ALLOWED_ORIGINS
from app.routes import analysis, predict, report

app = FastAPI(
    title="API — Apoio ao diagnóstico de câncer de mama",
    description=(
        "Serviço educacional de apoio à triagem. Não substitui diagnóstico, "
        "exame clínico ou a decisão de profissionais de saúde."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
