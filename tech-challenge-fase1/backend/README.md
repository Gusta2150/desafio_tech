# Backend — API de apoio ao diagnóstico de câncer de mama

API FastAPI que expõe o mesmo pipeline do notebook [`01_eda.ipynb`](../notebooks/01_eda.ipynb)
(validação → EDA → treino → avaliação → explicabilidade) para o frontend Angular
consumir. A lógica reutilizável vive em [`../src/pipeline.py`](../src/pipeline.py);
este backend só "serve" o que já está validado no notebook.

## Como rodar

```bash
# a partir de tech-challenge-fase1/
pip install -r backend/requirements.txt   # ou reaproveite o .venv do notebook +
                                           # pip install fastapi "uvicorn[standard]" python-multipart

cd backend
uvicorn app.main:app --reload --port 8000
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger) em
`http://localhost:8000/docs`.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/analysis` | Upload de CSV (`multipart/form-data`, campo `file`; opcional — sem arquivo usa `data/data.csv`). Roda o pipeline completo e devolve `analysis_id` + todos os resultados. |
| `POST` | `/api/predict` | Body `{ analysis_id, samples: [...], limiar? }`. Usa o modelo já treinado daquele `analysis_id` para prever novas amostras. |
| `GET` | `/api/report/pdf?analysis_id=...` | Gera e devolve o PDF (reaproveita `../scripts/generate_report_pdf.py`). |
| `GET` | `/api/health` | Healthcheck simples. |

## Notas

- CORS liberado para `http://localhost:4200` (porta padrão do `ng serve`) — ver
  `app/core.py` (`ALLOWED_ORIGINS`).
- O estado das análises fica em memória (`app/store.py`), suficiente para uma
  demo/vídeo com um único processo. Reiniciar o backend limpa os `analysis_id`
  já gerados.
- O notebook não foi alterado por este backend — `src/pipeline.py` espelha a
  mesma lógica das células 2.1/2.2/4.4–4.8, mas os dois não compartilham código
  em tempo de execução. Se um dia o notebook passar a importar essas mesmas
  funções, essa duplicação desaparece.
