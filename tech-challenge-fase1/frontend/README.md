# Frontend — Apoio ao diagnóstico de câncer de mama (Angular 16)

Interface web que consome a [API do backend](../backend/README.md) para
apresentar, de forma interativa, o mesmo fluxo do notebook
[`01_eda.ipynb`](../notebooks/01_eda.ipynb): upload de CSV, validação,
EDA, comparação de modelos, avaliação, explicabilidade e previsão.

Angular 16, componentes **standalone**, gráficos com **ng2-charts/Chart.js**.

## Como rodar

Pré-requisito: o [backend](../backend/README.md) rodando em `http://localhost:8000`
(ver `src/environments/environment.ts` para trocar a URL da API).

```bash
cd frontend
npm install --legacy-peer-deps   # necessário: ng2-charts declara peer dep de
                                  # @angular/cdk que conflita com Angular 16 no
                                  # resolver estrito do npm
npm start                        # = ng serve
```

Abra `http://localhost:4200`.

## Fluxo da aplicação

1. **Upload** (`/upload`) — envia um CSV ou usa o dataset padrão do projeto.
2. **Dashboard** (`/dashboard`) — abas com o resultado completo do pipeline:
   1. Validação (compatibilidade do CSV)
   2. EDA (distribuição, correlações, estatísticas descritivas)
   3. Modelagem (comparação Regressão Logística vs Random Forest)
   4. Avaliação (classification report, matriz de confusão, curva ROC)
   5. Explicabilidade (permutation importance, SHAP)
   6. Prever amostra (formulário manual, upload em lote, download do PDF)

## Estrutura

```
src/app/
├── core/           # tipos TS + AnalysisService (chamadas HTTP)
├── shared/         # componentes reaproveitados (aviso clínico)
└── pages/
    ├── upload/
    └── dashboard/  # shell de abas + um componente por aba
```

## Build de produção

```bash
npm run build
```
