# Tech Challenge — Fase 1
## Integrantes do Grupo
- Gabriel Wesley RM376899
- Gustavo Leite RM375733
- Luiz Fellipe RM376854 

## IA para Saúde e Segurança da Mulher

Sistema de suporte ao diagnóstico e detecção de riscos relacionados à saúde da
mulher, usando Machine Learning sobre dados estruturados (Breast Cancer
Wisconsin — diagnóstico de câncer de mama).

## Estrutura do projeto

```
tech-challenge-fase1/
├── data/           # dataset(s) usados (ou instruções de download)
├── notebooks/      # notebooks Jupyter (EDA, pré-processamento, modelagem)
├── src/            # código Python reutilizável (pipeline, funções auxiliares)
├── models/         # modelos treinados salvos (.pkl / .joblib)
├── reports/        # relatório técnico e imagens/gráficos exportados
├── scripts/        # utilitários (geração do PDF de análise diagnóstica)
├── backend/        # API FastAPI (opcional) — expõe o pipeline pro frontend
├── frontend/       # aplicação Angular 16 (opcional) — UI web do pipeline
├── requirements.txt
├── Dockerfile
└── README.md
```

## Aplicação web (opcional)

Além do notebook, o projeto tem uma interface web (Angular 16 + API FastAPI)
que roda o mesmo pipeline com upload de CSV. Ver
[`backend/README.md`](backend/README.md) e [`frontend/README.md`](frontend/README.md)
para instruções de execução.

## Como configurar o ambiente (local)

1. **Pré-requisitos**: Python 3.10+ instalado, VS Code com as extensões abaixo.
2. Criar e ativar um ambiente virtual:

   ```bash
   python -m venv .venv

   # macOS / Linux
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. Instalar as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Abrir a pasta no VS Code e selecionar o interpretador Python do `.venv`
   (Ctrl/Cmd+Shift+P → "Python: Select Interpreter").

5. Baixar o dataset (veja `data/README.md`) e colocá-lo em `data/`.

6. Abrir `notebooks/01_eda.ipynb` e rodar as células para conferir que tudo
   está funcionando.

## Como executar via Docker (opcional)

```bash
docker build -t tech-challenge-fase1 .
docker run -p 8888:8888 -v $(pwd):/app tech-challenge-fase1
```

Isso sobe um Jupyter Lab acessível em `http://localhost:8888`.

## Dataset

Breast Cancer Wisconsin (Diagnostic) — Kaggle:
https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data/data

Ver instruções de download em `data/README.md`.

## Equipe e divisão de tarefas

Ver o documento "Plano de Projeto" do grupo para cronograma e responsabilidades.

## Relatório técnico

O relatório técnico final (EDA, pré-processamento, modelos, resultados e
interpretação) ficará em `reports/relatorio_tecnico.md` (ou `.pdf`).

### Gerar o PDF da análise diagnóstica

Após executar o notebook até a seção **5.2**, execute:

```bash
python scripts/generate_report_pdf.py
```

O arquivo será gerado em `reports/analise_diagnostica_cancer_mama.pdf` com o
status de compatibilidade do CSV, a distribuição dos diagnósticos e as métricas
da última execução. Para usar outro
arquivo de origem ou destino:

```bash
python scripts/generate_report_pdf.py \
  --source reports/analise_diagnostica.md \
  --output reports/analise_diagnostica_cancer_mama.pdf
```
