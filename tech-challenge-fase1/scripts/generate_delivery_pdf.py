"""Gera o PDF de entrega da Fase 1 — uma capa simples com o link do
repositório e o link do vídeo de demonstração no YouTube.

Este é um documento separado do relatório técnico (`analise_diagnostica_
cancer_mama.pdf`, gerado por `generate_report_pdf.py`). Ele existe só para
atender ao formato pedido pelo enunciado: um PDF curto com os dois links
principais da entrega.

Uso:
    python scripts/generate_delivery_pdf.py --video-url "https://youtu.be/SEU_ID"

Sem `--video-url`, gera com um placeholder — rode de novo passando a URL
real assim que o vídeo estiver no ar.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from generate_report_pdf import INTEGRANTES, REPOSITORIO_URL

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_DIR / "reports" / "entrega_fase1.pdf"
VIDEO_PLACEHOLDER = "https://youtu.be/SEU-VIDEO-AQUI"


def build_delivery_pdf(output_path: Path, *, repositorio_url: str, video_url: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "Titulo", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=27, alignment=TA_CENTER, spaceAfter=6,
        textColor=colors.HexColor("#1f4e78"),
    )
    subtitulo_style = ParagraphStyle(
        "Subtitulo", parent=base["Normal"], fontName="Helvetica",
        fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=28,
        textColor=colors.HexColor("#4b5563"),
    )
    rotulo_style = ParagraphStyle(
        "Rotulo", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, textColor=colors.white,
    )
    link_style = ParagraphStyle(
        "Link", parent=base["Normal"], fontName="Helvetica",
        fontSize=12, leading=16, textColor=colors.HexColor("#1f4e78"),
    )
    integrantes_style = ParagraphStyle(
        "Integrantes", parent=base["Normal"], fontName="Helvetica",
        fontSize=10.5, leading=15, alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
    )

    def _link_card(rotulo: str, url: str) -> Table:
        linha = [
            [Paragraph(escape(rotulo), rotulo_style)],
            [Paragraph(f'<link href="{escape(url)}">{escape(url)}</link>', link_style)],
        ]
        tabela = Table(linha, colWidths=[15 * cm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#9ca3af")),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        return tabela

    documento = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=4 * cm, bottomMargin=4 * cm,
        title="Entrega — Tech Challenge Fase 1",
        author="Tech Challenge — Fase 1",
    )

    conteudo = [
        Paragraph("Tech Challenge — Fase 1", titulo_style),
        Paragraph(
            "Sistema de apoio à classificação de câncer de mama",
            subtitulo_style,
        ),
        _link_card("Repositório do projeto (código-fonte, README, Dockerfile, dataset e relatório técnico)", repositorio_url),
        Spacer(1, 18),
        _link_card("Vídeo de demonstração (YouTube)", video_url),
        Spacer(1, 36),
        Paragraph("Integrantes", ParagraphStyle(
            "IntegrantesTitulo", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=15, alignment=TA_CENTER,
            textColor=colors.HexColor("#374151"), spaceAfter=4,
        )),
        Paragraph(" • ".join(escape(nome) for nome in INTEGRANTES), integrantes_style),
    ]

    documento.build(conteudo)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o PDF de entrega (links de repositório e vídeo).")
    parser.add_argument("--repo-url", default=REPOSITORIO_URL, help="URL do repositório Git.")
    parser.add_argument("--video-url", default=VIDEO_PLACEHOLDER, help="URL do vídeo de demonstração no YouTube.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Arquivo PDF de destino.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    build_delivery_pdf(args.output, repositorio_url=args.repo_url, video_url=args.video_url)
    print(f"PDF de entrega gerado em: {args.output}")
    if args.video_url == VIDEO_PLACEHOLDER:
        print(
            "Aviso: o link do vídeo ainda é um placeholder. Rode de novo com "
            "--video-url \"<link real do YouTube>\" quando o vídeo estiver publicado."
        )
