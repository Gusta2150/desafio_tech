"""Gera o PDF de análise diagnóstica (câncer de mama).

Um único gerador (`build_pdf`), usado tanto pela célula 5.2 do notebook
(`notebooks/01_eda.ipynb`) quanto pela API web (`backend/app/routes/report.py`)
— assim os dois produzem exatamente o mesmo documento a partir dos mesmos
dados de entrada, em vez de duas versões divergentes.

Rodar como script (`python scripts/generate_report_pdf.py`) regenera o PDF a
partir do último resumo salvo em `reports/resumo_analise_diagnostica.json` +
gráficos em `reports/pdf_assets/` — útil pra conferir o resultado sem precisar
rodar o notebook ou subir o backend de novo.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_DIR / "reports" / "analise_diagnostica_cancer_mama.pdf"
DEFAULT_SUMMARY = PROJECT_DIR / "reports" / "resumo_analise_diagnostica.json"
DEFAULT_ASSETS_DIR = PROJECT_DIR / "reports" / "pdf_assets"

INTEGRANTES = ["Gustavo Leite", "Luiz Fellipe", "Gabriel Wesley"]
REPOSITORIO_URL = "https://github.com/Gusta2150/desafio_tech"

# Legendas fixas dos 4 gráficos, na ordem em que aparecem no PDF — usadas
# tanto pelo CLI (que só acha os arquivos .png) quanto como referência do
# que `src.pipeline.render_report_charts` já devolve pronto.
_GRAFICO_LEGENDAS: dict[str, tuple[str, str]] = {
    "distribuicao_diagnosticos.png": (
        "Distribuição dos diagnósticos",
        "O gráfico mostra a quantidade de casos benignos e malignos presentes na base.",
    ),
    "correlacao_malignidade.png": (
        "Correlação com malignidade",
        "A correlação mostra associação estatística com o diagnóstico, mas não demonstra causa clínica.",
    ),
    "matriz_confusao.png": (
        "Matriz de confusão",
        "A matriz mostra os acertos e erros do modelo, incluindo falsos positivos e falsos negativos.",
    ),
    "importancia_atributos.png": (
        "Importância por permutação",
        "Este gráfico mostra quais atributos mais impactaram o desempenho do modelo.",
    ),
}


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "Titulo", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=19, leading=23, alignment=TA_CENTER, spaceAfter=16,
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, spaceBefore=10, spaceAfter=7,
        ),
        "texto": ParagraphStyle(
            "Texto", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=14, spaceAfter=8,
        ),
        "link": ParagraphStyle(
            "Link", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=14, spaceAfter=8, textColor=colors.HexColor("#1f4e78"),
        ),
    }


def _texto(valor: Any, estilo: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(valor)), estilo)


def _tabela(linhas: list[list[Paragraph]], larguras: tuple[float, float] = (6.2 * cm, 10.2 * cm)) -> Table:
    tabela = Table(linhas, colWidths=list(larguras))
    tabela.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9ca3af")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    return tabela


def _numero_pagina(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4b5563"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Página {document.page}")
    canvas.restoreState()


def build_pdf(
    output_path: Path,
    *,
    identificacao_csv: dict[str, Any],
    total_amostras: int,
    total_atributos: int,
    quantidade_benigno: int,
    quantidade_maligno: int,
    modelo_selecionado: str,
    metricas_modelo: dict[str, float],
    descricao_divisao: str,
    origem_teste: str,
    graficos: list[tuple[str, Path, str]] | None = None,
    integrantes: list[str] | None = None,
) -> None:
    """Monta e salva o PDF de análise diagnóstica.

    Única função que define o conteúdo do relatório — chamada pela célula 5.2
    do notebook e por `backend/app/routes/report.py`, sempre com este mesmo
    layout. Qualquer mudança no relatório deve ser feita aqui, não duplicada
    nos dois lugares.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = _build_styles()
    graficos = graficos or []
    integrantes = integrantes or INTEGRANTES

    documento = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title="Análise Diagnóstica de Câncer de Mama",
        author="Tech Challenge — Fase 1",
    )

    conteudo: list[Any] = []

    conteudo.append(_texto("Análise Diagnóstica de Câncer de Mama", styles["titulo"]))

    conteudo.append(_texto("Integrantes", styles["subtitulo"]))
    for nome in integrantes:
        conteudo.append(_texto(f"• {nome}", styles["texto"]))
    conteudo.append(Paragraph(
        f'Repositório: <link href="{escape(REPOSITORIO_URL)}">{escape(REPOSITORIO_URL)}</link>',
        styles["link"],
    ))
    conteudo.append(Spacer(1, 8))

    conteudo.append(_texto("Identificação do CSV", styles["subtitulo"]))
    conteudo.append(_tabela([
        [_texto("Campo", styles["texto"]), _texto("Resultado", styles["texto"])],
        [_texto("Status", styles["texto"]), _texto(identificacao_csv.get("status", "Não informado"), styles["texto"])],
        [_texto("Domínio identificado", styles["texto"]), _texto(identificacao_csv.get("dominio_identificado", "Não informado"), styles["texto"])],
        [_texto("Mensagem", styles["texto"]), _texto(identificacao_csv.get("mensagem", "Não informado"), styles["texto"])],
    ]))
    conteudo.append(Spacer(1, 10))

    conteudo.append(_texto("Discussão da análise exploratória", styles["subtitulo"]))
    conteudo.append(_texto(
        f"A base analisada possui {total_amostras} amostras e {total_atributos} atributos "
        "utilizados na classificação. Foram analisados tipos de dados, valores "
        "ausentes, estatísticas descritivas, distribuição das classes e correlação "
        "entre características morfológicas e malignidade.",
        styles["texto"],
    ))
    conteudo.append(_texto(
        "A análise exploratória é importante porque permite identificar problemas "
        "nos dados antes do treinamento, como valores ausentes, escalas diferentes "
        "entre atributos e possível desbalanceamento entre diagnósticos.",
        styles["texto"],
    ))

    conteudo.append(_texto("Distribuição dos diagnósticos", styles["subtitulo"]))
    conteudo.append(_tabela([
        [_texto("Classe", styles["texto"]), _texto("Quantidade", styles["texto"])],
        [_texto("Benigno", styles["texto"]), _texto(quantidade_benigno, styles["texto"])],
        [_texto("Maligno", styles["texto"]), _texto(quantidade_maligno, styles["texto"])],
    ]))
    conteudo.append(Spacer(1, 10))

    conteudo.append(_texto("Estratégias de pré-processamento", styles["subtitulo"]))
    conteudo.append(_texto(
        "O pré-processamento remove identificadores sem valor preditivo, elimina "
        "colunas totalmente vazias, trata valores ausentes com mediana para campos "
        "numéricos e valor mais frequente para campos categóricos. As variáveis "
        "numéricas são normalizadas com StandardScaler e variáveis categóricas, "
        "quando existirem, são convertidas com OneHotEncoder.",
        styles["texto"],
    ))
    conteudo.append(_texto(
        "Os dados são separados de forma estratificada entre treino e teste. "
        "A proporção padrão é de aproximadamente 80% para treino e 20% para teste. "
        "Entretanto, quando a base possui poucas amostras, o sistema adapta "
        "automaticamente o tamanho do conjunto de teste para garantir que exista "
        "pelo menos um caso benigno e um caso maligno nos dois grupos.",
        styles["texto"],
    ))
    conteudo.append(_texto(descricao_divisao, styles["texto"]))

    conteudo.append(_texto("Modelos utilizados e justificativa", styles["subtitulo"]))
    conteudo.append(_texto(
        "Foram utilizados dois algoritmos. A Regressão Logística foi escolhida "
        "por ser um modelo mais simples, interpretável e capaz de gerar "
        "probabilidades. O Random Forest foi escolhido por capturar relações "
        "não lineares e interações mais complexas entre os atributos.",
        styles["texto"],
    ))
    conteudo.append(_texto(f"O modelo selecionado nesta execução foi: {modelo_selecionado}.", styles["texto"]))

    conteudo.append(_texto("Resultados do modelo", styles["subtitulo"]))
    if metricas_modelo:
        linhas_metricas = [[_texto("Métrica", styles["texto"]), _texto("Valor", styles["texto"])]]
        for metrica, valor in metricas_modelo.items():
            linhas_metricas.append([_texto(metrica, styles["texto"]), _texto(f"{valor:.3f}", styles["texto"])])
        conteudo.append(_tabela(linhas_metricas))
    else:
        conteudo.append(_texto(
            "As métricas não estão disponíveis. Execute as células de modelagem "
            "antes de gerar o PDF.",
            styles["texto"],
        ))
    conteudo.append(_texto(
        "O recall de malignidade é uma métrica prioritária porque indica quantos "
        "casos malignos presentes foram identificados pelo modelo. Accuracy, "
        "F1-score e ROC-AUC são analisados em conjunto para evitar interpretações isoladas.",
        styles["texto"],
    ))

    conteudo.append(_texto("Interpretação dos resultados", styles["subtitulo"]))
    accuracy = metricas_modelo.get("accuracy")
    recall = metricas_modelo.get("recall_maligno")
    f1 = metricas_modelo.get("f1_maligno")
    roc_auc = metricas_modelo.get("roc_auc")
    if None not in (accuracy, recall, f1, roc_auc):
        conteudo.append(_texto(
            f"Na execução atual, o modelo selecionado foi {modelo_selecionado}. "
            f"A accuracy obtida foi {accuracy:.3f}, indicando a proporção geral "
            f"de classificações corretas no conjunto de teste. "
            f"O recall para malignidade foi {recall:.3f}, representando a "
            f"proporção de casos malignos identificados corretamente. "
            f"O F1-score foi {f1:.3f}, mostrando o equilíbrio entre precisão "
            f"e recall. A métrica ROC-AUC foi {roc_auc:.3f}, indicando a "
            f"capacidade de diferenciar padrões benignos e malignos.",
            styles["texto"],
        ))
        conteudo.append(_texto(
            "Esses resultados representam desempenho técnico na base utilizada. "
            "Eles não representam validação clínica e não confirmam que o "
            "sistema terá o mesmo desempenho em outros hospitais, populações "
            "ou equipamentos.",
            styles["texto"],
        ))
    else:
        conteudo.append(_texto(
            "Não foi possível interpretar os resultados porque as métricas do "
            "modelo não estão disponíveis.",
            styles["texto"],
        ))

    conteudo.append(_texto("Origem dos testes", styles["subtitulo"]))
    conteudo.append(_texto(origem_teste, styles["texto"]))

    if graficos:
        conteudo.append(PageBreak())
        conteudo.append(_texto("Resultados obtidos: gráficos e análises", styles["subtitulo"]))
        for titulo_grafico, caminho_grafico, explicacao in graficos:
            conteudo.append(_texto(titulo_grafico, styles["subtitulo"]))
            conteudo.append(Image(str(caminho_grafico), width=16 * cm, height=9 * cm))
            conteudo.append(_texto(explicacao, styles["texto"]))

    conteudo.append(_texto("Medidas que mais influenciaram a classificação", styles["subtitulo"]))
    conteudo.append(_texto(
        "Além de informar a probabilidade de uma amostra ser classificada como "
        "benigna ou maligna, o sistema analisa quais medidas tiveram maior "
        "influência no resultado. Entre elas podem aparecer raio, textura, "
        "área, perímetro, concavidade e simetria da massa mamária.",
        styles["texto"],
    ))
    conteudo.append(_texto(
        "A importância por permutação mostra quais atributos são mais relevantes "
        "para o desempenho geral do modelo. O SHAP complementa essa análise ao "
        "mostrar como cada atributo pode aumentar ou reduzir a probabilidade "
        "estimada em uma previsão específica.",
        styles["texto"],
    ))
    conteudo.append(_texto(
        "Essas informações ajudam a tornar o resultado mais compreensível para "
        "a análise humana. Entretanto, elas não comprovam que uma característica "
        "causou câncer e não substituem avaliação médica, exames de imagem ou biópsia.",
        styles["texto"],
    ))

    conteudo.append(_texto("Interpretação e limites clínicos", styles["subtitulo"]))
    conteudo.append(_texto(
        "Esta análise é apoio educacional à triagem. O resultado não substitui "
        "consulta médica, mamografia, biópsia, histórico clínico ou protocolos "
        "assistenciais. Probabilidade baixa não exclui câncer e probabilidade alta "
        "não confirma câncer. A decisão final deve ser tomada por profissionais de saúde.",
        styles["texto"],
    ))

    documento.build(conteudo, onFirstPage=_numero_pagina, onLaterPages=_numero_pagina)


def _collect_graficos_from_assets(assets_dir: Path) -> list[tuple[str, Path, str]]:
    """Acha os 4 PNGs conhecidos em `assets_dir`, na ordem fixa do relatório."""
    graficos = []
    for filename, (titulo, legenda) in _GRAFICO_LEGENDAS.items():
        caminho = assets_dir / filename
        if caminho.exists():
            graficos.append((titulo, caminho, legenda))
    return graficos


def generate_from_summary(summary_path: Path, output_path: Path, assets_dir: Path | None = None) -> None:
    """Lê `resumo_analise_diagnostica.json` (+ imagens em `pdf_assets/`) e gera
    o PDF. Usado pelo CLI standalone (`python scripts/generate_report_pdf.py`)
    e, se preciso, por quem quiser regenerar o PDF sem rodar tudo de novo."""
    if not summary_path.exists():
        raise FileNotFoundError(
            f"Resumo não encontrado: {summary_path}. Rode o notebook até a seção "
            "5.2, ou gere uma análise pelo frontend, antes de regenerar o PDF."
        )

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assets_dir = assets_dir or summary_path.parent / "pdf_assets"
    identificacao_csv = summary.get("identificacao_csv", {})
    distribuicao = summary.get("distribuicao_diagnostico", {})
    metricas = summary.get("metricas_modelo", {})

    build_pdf(
        output_path,
        identificacao_csv=identificacao_csv,
        total_amostras=identificacao_csv.get("amostras", 0),
        total_atributos=identificacao_csv.get("atributos", 0),
        quantidade_benigno=distribuicao.get("Benigno", 0),
        quantidade_maligno=distribuicao.get("Maligno", 0),
        modelo_selecionado=summary.get("modelo_selecionado", "Modelo não treinado"),
        metricas_modelo=metricas,
        descricao_divisao=summary.get("descricao_divisao", "A divisão entre treino e teste não foi executada nesta sessão."),
        origem_teste=summary.get("origem_testes", "Não informada"),
        graficos=_collect_graficos_from_assets(assets_dir),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o PDF de análise diagnóstica a partir do último resumo salvo.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="Resumo JSON da execução.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Arquivo PDF de destino.")
    parser.add_argument("--assets-dir", type=Path, default=None, help="Pasta com os gráficos .png (padrão: reports/pdf_assets).")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    generate_from_summary(args.summary, args.output, args.assets_dir)
    print(f"PDF gerado em: {args.output}")
