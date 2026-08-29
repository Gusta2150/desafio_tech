"""GET /api/report/pdf — gera o mesmo PDF da seção 5.2 do notebook, via API.

Usa `src.pipeline.render_report_charts` (mesmos gráficos) e
`scripts/generate_report_pdf.build_pdf` (mesmo layout) que o notebook chama —
um único gerador, dois lugares que o disparam.
"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core import REPORTS_DIR
from app.store import analyses
from generate_report_pdf import build_pdf  # scripts/generate_report_pdf.py
from src.pipeline import build_split_description, render_report_charts

router = APIRouter(tags=["report"])


@router.get("/report/pdf")
def download_report_pdf(analysis_id: str):
    analysis = analyses.get(analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="analysis_id não encontrado. Rode POST /api/analysis primeiro.",
        )

    if analysis.trainable and analysis.results_df is not None:
        metricas_modelo = {
            key: float(value)
            for key, value in analysis.results_df.iloc[0].drop(labels="modelo").items()
        }
        modelo_selecionado = analysis.best_name
    else:
        metricas_modelo = {}
        modelo_selecionado = "Não treinado (amostras insuficientes — ver identificacao_csv)"

    total_amostras = int(analysis.identificacao_csv.get("amostras", 0))
    total_teste = len(analysis.X_test) if analysis.X_test is not None else 0
    total_treino = max(total_amostras - total_teste, 0)
    descricao_divisao = build_split_description(total_treino, total_teste)

    graficos = []
    if analysis.X is not None and analysis.y is not None:
        assets_dir = REPORTS_DIR / "pdf_assets"
        importance_records = (
            analysis.explainability.get("permutation_importance") if analysis.trainable else None
        )
        graficos = render_report_charts(
            assets_dir,
            X=analysis.X,
            y=analysis.y,
            best_model=analysis.best_model,
            X_test=analysis.X_test,
            y_test=analysis.y_test,
            modelo_selecionado=modelo_selecionado or "Modelo não treinado",
            importance_records=importance_records,
        )

    resumo_analise = {
        "identificacao_csv": analysis.identificacao_csv,
        "distribuicao_diagnostico": analysis.eda["diagnosis_distribution"],
        "modelo_selecionado": modelo_selecionado,
        "metricas_modelo": metricas_modelo,
        "descricao_divisao": descricao_divisao,
        "origem_testes": "Análise gerada via aplicação web (upload de CSV)",
        "aviso_clinico": (
            "Esta análise é apoio educacional à triagem e não substitui a "
            "avaliação de profissionais de saúde."
        ),
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = REPORTS_DIR / "resumo_analise_diagnostica.json"
    summary_path.write_text(
        json.dumps(resumo_analise, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    output_path = REPORTS_DIR / "analise_diagnostica_cancer_mama.pdf"
    build_pdf(
        output_path,
        identificacao_csv=analysis.identificacao_csv,
        total_amostras=total_amostras,
        total_atributos=len(analysis.X_columns),
        quantidade_benigno=analysis.eda["diagnosis_distribution"].get("Benigno", 0),
        quantidade_maligno=analysis.eda["diagnosis_distribution"].get("Maligno", 0),
        modelo_selecionado=modelo_selecionado or "Modelo não treinado",
        metricas_modelo=metricas_modelo,
        descricao_divisao=descricao_divisao,
        origem_teste="Análise gerada via aplicação web (upload de CSV)",
        graficos=graficos,
    )

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename="analise_diagnostica_cancer_mama.pdf",
    )
