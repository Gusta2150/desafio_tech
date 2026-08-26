# Sistema de apoio à classificação de câncer de mama

## Integrantes

- Gabriel Wesley RM376899
- Gustavo Leite RM375733
- Luiz Fellipe RM376854 

---

## Visão geral

Este projeto utiliza Machine Learning para analisar dados estruturados relacionados a massas mamárias e apoiar a classificação técnica de registros como:

- `B` / benigno;
- `M` / maligno.

A solução utiliza atributos numéricos como raio, textura, perímetro, área, concavidade, simetria e outras medidas morfológicas.

> Importante: este projeto é educacional e de apoio à triagem. Ele não substitui avaliação médica, exames clínicos, mamografia, biópsia ou decisão de profissionais de saúde.

---

## Objetivo

Construir uma solução inicial de Inteligência Artificial aplicada à saúde feminina, utilizando Machine Learning para identificar padrões associados a diagnósticos benignos e malignos de câncer de mama.

O sistema realiza:

- validação de compatibilidade do CSV com câncer de mama;
- análise exploratória dos dados;
- tratamento e preparação dos dados;
- treinamento de modelos de classificação;
- comparação entre algoritmos;
- avaliação com métricas;
- explicabilidade das previsões;
- testes com novos dados;
- geração de PDF com análise diagnóstica.

---

## Estrutura do projeto

```text
tech-challenge-fase1/
├── data/
│   ├── data.csv
│   ├── cancer_mama_1_diagnostico.csv
│   ├── breast_cancer_data.csv
│   └── outros_datasets.csv
├── notebooks/
│   └── 01_eda.ipynb
├── models/
│   └── modelo_cancer_mama.joblib
├── reports/
│   ├── relatorio_tecnico.md
│   └── analise_diagnostica_cancer_mama.pdf
├── scripts/
│   └── generate_report_pdf.py
├── src/
│   └── data_utils.py
├── requirements.txt
├── Dockerfile
└── README.md
