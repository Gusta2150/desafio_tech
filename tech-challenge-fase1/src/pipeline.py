"""Pipeline reutilizável de câncer de mama.

Esta é a mesma lógica das seções 2.1, 2.2 e 4.4–4.8 de
``notebooks/01_eda.ipynb``, extraída para funções puras para que o backend
web (``backend/``) possa reaproveitá-la sem duplicar código. O notebook em si
não foi alterado por este módulo.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    accuracy_score,
    f1_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
TARGET = "diagnosis"

# Mesmos rótulos aceitos pela célula 2.1 do notebook
LABEL_MAP = {
    "m": "M",
    "malignant": "M",
    "maligno": "M",
    "b": "B",
    "benign": "B",
    "benigno": "B",
}

# Mesmo conjunto de colunas esperadas pela célula 2.2 do notebook
EXPECTED_BREAST_FEATURES = {
    "radius_mean", "texture_mean", "perimeter_mean", "area_mean",
    "concavity_mean", "radius_worst", "area_worst",
}

# Mínimo de amostras por classe para treinar com split estratificado 80/20
# com alguma confiabilidade. Abaixo disso, o próprio scikit-learn já rejeita
# o split (não há amostras suficientes pra representar as 2 classes no teste).
MIN_SAMPLES_PER_CLASS = 10

CLINICAL_DISCLAIMER = (
    "Resultado de apoio educacional à triagem. Não confirma nem descarta "
    "câncer e não substitui a avaliação de profissionais de saúde."
)


class IncompatibleDatasetError(ValueError):
    """Levantado quando o CSV não tem os campos/rótulos esperados."""

    def __init__(self, message: str, details: dict[str, Any]):
        super().__init__(message)
        self.details = details


@dataclass
class TrainedAnalysis:
    """Estado guardado em memória para uma análise (upload) já processada.

    Quando ``trainable`` é ``False`` (amostras insuficientes pra treinar um
    modelo novo — ver ``check_trainable``), só ``identificacao_csv``, ``eda``
    e ``X_columns`` ficam preenchidos; os campos de modelo/avaliação ficam
    ``None``/vazios. É um resultado válido, não um erro: o arquivo foi
    validado e explorado normalmente, só não há dados de sobra pra treinar.
    """

    identificacao_csv: dict[str, Any]
    eda: dict[str, Any]
    X_columns: list[str]
    X: pd.DataFrame | None = None
    y: pd.Series | None = None
    results_df: pd.DataFrame | None = None
    fitted_models: dict[str, Pipeline] | None = None
    best_name: str | None = None
    best_model: Pipeline | None = None
    X_test: pd.DataFrame | None = None
    y_test: pd.Series | None = None
    evaluation: dict[str, Any] = field(default_factory=dict)
    explainability: dict[str, Any] = field(default_factory=dict)
    trainable: bool = True
    trainable_issue: dict[str, Any] | None = None


def load_and_validate(file_bytes: bytes) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Lê o CSV, normaliza rótulos e devolve (data, y, X). Espelha a célula 2.1."""
    raw_data = pd.read_csv(io.BytesIO(file_bytes))
    data = raw_data.dropna(axis=1, how="all").copy()
    data = data.drop(columns=["id"], errors="ignore")

    if TARGET not in data.columns:
        raise IncompatibleDatasetError(
            "A base precisa conter a coluna 'diagnosis' com os rótulos M e B.",
            {
                "status": "CSV incompatível",
                "dominio_identificado": "Não é câncer de mama",
                "mensagem": (
                    "Este arquivo não contém informações de diagnóstico de câncer "
                    "de mama (não encontramos a coluna 'diagnosis', que indica se "
                    "o caso é benigno ou maligno)."
                ),
            },
        )

    data[TARGET] = data[TARGET].astype("string").str.strip().str.lower()
    found_labels = set(data[TARGET].dropna().unique())
    invalid_labels = found_labels - set(LABEL_MAP.keys())
    if invalid_labels:
        raise IncompatibleDatasetError(
            f"Rótulos inesperados em diagnosis: {invalid_labels}.",
            {
                "status": "CSV incompatível",
                "dominio_identificado": "Não é câncer de mama",
                "mensagem": (
                    "A coluna 'diagnosis' existe, mas tem valores que não "
                    f"reconhecemos ({', '.join(sorted(invalid_labels))}). Os "
                    "valores aceitos são M, B, malignant, benign, maligno ou "
                    "benigno."
                ),
            },
        )
    data[TARGET] = data[TARGET].map(LABEL_MAP)

    y = data[TARGET].map({"M": 1, "B": 0})
    X = data.drop(columns=TARGET)
    return data, y, X


def check_compatibility(data: pd.DataFrame, X: pd.DataFrame) -> dict[str, Any]:
    """Espelha a célula 2.2: confere colunas morfológicas esperadas."""
    missing_features = sorted(EXPECTED_BREAST_FEATURES - set(data.columns))
    if missing_features:
        raise IncompatibleDatasetError(
            "Base incompatível com câncer de mama.",
            {
                "status": "CSV incompatível",
                "dominio_identificado": "Não é câncer de mama",
                "mensagem": (
                    "Este arquivo não tem as medidas que esse sistema espera de "
                    "um exame de câncer de mama (como tamanho, textura e formato "
                    "das células)."
                ),
                "campos_ausentes": missing_features,
            },
        )
    return {
        "status": "CSV compatível",
        "dominio_identificado": "Câncer de mama",
        "mensagem": "Campos e rótulos compatíveis com o modelo Breast Cancer Wisconsin.",
        "amostras": int(len(data)),
        "atributos": int(X.shape[1]),
    }


def run_eda(data: pd.DataFrame, X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    """Espelha as seções 3.2–3.4 / 4.3: describe, nulos, distribuição, correlações."""
    describe = X.describe().round(4).to_dict()
    missing = X.isna().sum().loc[lambda s: s.gt(0)].to_dict()
    distribution = {
        "Benigno": int((y == 0).sum()),
        "Maligno": int((y == 1).sum()),
    }

    correlations = pd.concat([X, y.rename("maligno")], axis=1).corr(numeric_only=True)["maligno"].drop("maligno")
    top_correlations = correlations.abs().sort_values(ascending=False).head(10).index.tolist()
    top_correlation_values = {feature: round(float(correlations[feature]), 4) for feature in top_correlations}
    correlation_matrix = X.loc[:, top_correlations].corr().round(4).to_dict()

    return {
        "describe": describe,
        "missing_values": missing,
        "diagnosis_distribution": distribution,
        "top_correlations": top_correlation_values,
        "correlation_matrix_top_features": correlation_matrix,
    }


def check_trainable(y: pd.Series) -> dict[str, Any] | None:
    """Confere se dá pra treinar um modelo novo com esse `y` (2 classes, amostras suficientes).

    Não lança exceção — devolve `None` se treinável, ou um dict de
    status/mensagem explicando o motivo. Um CSV pequeno (poucas linhas,
    ex.: 3-5 amostras separadas pra testar previsão) é um caso válido, só
    que para *prever*, não para *treinar do zero* — treinar exige um split
    estratificado com amostras de sobra em cada classe. Sem essa checagem,
    o scikit-learn levantaria um erro técnico cru (`ValueError: The
    test_size = 1 should be greater or equal to the number of classes = 2`,
    ou `needs samples of at least 2 classes`) direto pro usuário.
    """
    counts = y.value_counts()
    insufficient = counts[counts < MIN_SAMPLES_PER_CLASS]

    if len(counts) < 2 or not insufficient.empty:
        labels = {0: "Benigno", 1: "Maligno"}
        resumo = ", ".join(f"{labels.get(idx, idx)}: {int(qtd)}" for idx, qtd in counts.items())
        return {
            "status": "Amostras insuficientes para treinar",
            "mensagem": (
                f"Este arquivo tem poucas amostras por classe para treinar um modelo novo "
                f"({resumo} — mínimo recomendado: {MIN_SAMPLES_PER_CLASS} por classe). "
                "Mostrando apenas a validação e a análise exploratória deste arquivo. Para "
                "ver modelagem, avaliação e explicabilidade, use o dataset padrão do projeto "
                "(ou outro arquivo com mais amostras); para testar a previsão destas amostras "
                "específicas com o modelo já treinado, use a aba \"Prever amostra\" → "
                "\"Previsão em lote\"."
            ),
        }
    return None


def validate_trainable(y: pd.Series) -> None:
    """Versão que lança `IncompatibleDatasetError` — mantida para quem chama `split_and_train`
    diretamente e espera que amostras insuficientes interrompam a execução."""
    issue = check_trainable(y)
    if issue is not None:
        raise IncompatibleDatasetError(
            "Amostras insuficientes para treinar um novo modelo.",
            {
                "status": issue["status"],
                "dominio_identificado": "Câncer de mama (poucos dados para treinar)",
                "mensagem": issue["mensagem"],
            },
        )


def split_and_train(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, dict[str, Pipeline], pd.DataFrame, pd.Series]:
    """Espelha as células 4.4/4.5: split estratificado + LogReg + Random Forest."""
    validate_trainable(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )

    numeric_features = X_train.select_dtypes(include=np.number).columns.tolist()
    categorical_features = X_train.select_dtypes(exclude=np.number).columns.tolist()

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    models = {
        "Regressão Logística": LogisticRegression(
            max_iter=2_000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=500, min_samples_leaf=2, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }

    fitted_models: dict[str, Pipeline] = {}
    results = []
    for name, estimator in models.items():
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        probabilities = pipeline.predict_proba(X_test)[:, 1]
        fitted_models[name] = pipeline
        results.append({
            "modelo": name,
            "accuracy": accuracy_score(y_test, predictions),
            "recall_maligno": recall_score(y_test, predictions, pos_label=1),
            "f1_maligno": f1_score(y_test, predictions, pos_label=1),
            "roc_auc": roc_auc_score(y_test, probabilities),
        })

    results_df = pd.DataFrame(results).sort_values(
        ["recall_maligno", "f1_maligno", "roc_auc"], ascending=False
    ).reset_index(drop=True)

    return results_df, fitted_models, X_test, y_test


def evaluate(best_model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    """Espelha a célula 4.6: classification report, matriz de confusão, curva ROC."""
    predictions = best_model.predict(X_test)
    probabilities = best_model.predict_proba(X_test)[:, 1]

    report = classification_report(
        y_test, predictions, target_names=["Benigno", "Maligno"],
        digits=3, output_dict=True,
    )
    matrix = confusion_matrix(y_test, predictions).tolist()
    fpr, tpr, _ = roc_curve(y_test, probabilities)
    # Reduz a curva a ~50 pontos pra não inflar o payload
    step = max(1, len(fpr) // 50)
    roc_points = [{"fpr": round(float(f), 4), "tpr": round(float(t), 4)} for f, t in zip(fpr[::step], tpr[::step])]

    return {
        "classification_report": report,
        "confusion_matrix": {
            "labels": ["Benigno", "Maligno"],
            "matrix": matrix,
        },
        "roc_curve": roc_points,
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
    }


def explain(best_model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    """Espelha a célula 4.7: permutation importance + SHAP (com fallback)."""
    permutation = permutation_importance(
        best_model, X_test, y_test, scoring="recall",
        n_repeats=15, random_state=RANDOM_STATE, n_jobs=-1,
    )
    importance_df = pd.DataFrame({
        "atributo": X_test.columns,
        "importancia_media": permutation.importances_mean,
        "desvio_padrao": permutation.importances_std,
    }).sort_values("importancia_media", ascending=False).head(12)

    result: dict[str, Any] = {
        "permutation_importance": [
            {
                "atributo": row.atributo,
                "importancia_media": round(float(row.importancia_media), 5),
                "desvio_padrao": round(float(row.desvio_padrao), 5),
            }
            for row in importance_df.itertuples()
        ],
        "shap": None,
        "shap_error": None,
    }

    try:
        import shap

        transformed_train_sample = best_model.named_steps["preprocessor"].transform(X_test)
        feature_names = best_model.named_steps["preprocessor"].get_feature_names_out()
        estimator = best_model.named_steps["model"]

        explainer = shap.Explainer(estimator, transformed_train_sample, feature_names=feature_names)
        shap_values = explainer(transformed_train_sample[: min(50, len(X_test))])
        values = shap_values[..., 1] if shap_values.values.ndim == 3 else shap_values
        mean_abs = np.abs(values.values).mean(axis=0)
        shap_ranking = sorted(
            zip(feature_names, mean_abs.tolist()), key=lambda item: item[1], reverse=True
        )[:12]
        result["shap"] = [
            {"atributo": name, "impacto_medio_absoluto": round(float(value), 5)}
            for name, value in shap_ranking
        ]
    except ImportError:
        result["shap_error"] = "SHAP não está instalado no ambiente do backend."
    except Exception as error:  # pragma: no cover - mesma tolerância do notebook
        result["shap_error"] = f"Não foi possível gerar SHAP nesta execução: {error}"

    return result


def predict_samples(
    best_model: Pipeline, X_columns: list[str], amostras: pd.DataFrame, limiar: float = 0.50
) -> pd.DataFrame:
    """Espelha a função prever_risco_cancer_mama da célula 4.8."""
    if not 0 < limiar < 1:
        raise ValueError("O limiar deve estar entre 0 e 1.")

    missing_columns = sorted(set(X_columns) - set(amostras.columns))
    if missing_columns:
        raise IncompatibleDatasetError(
            "Amostra incompatível com o modelo de câncer de mama.",
            {
                "status": "Entrada incompatível",
                "colunas_ausentes": missing_columns,
                "mensagem": (
                    "Este arquivo não possui os campos esperados pelo modelo. "
                    "Nenhuma previsão foi realizada; isso não confirma nem "
                    "descarta câncer de mama."
                ),
            },
        )

    input_data = amostras.loc[:, X_columns].copy()
    probability = best_model.predict_proba(input_data)[:, 1]
    triage = np.where(
        probability >= limiar, "Encaminhar para avaliação médica", "Sem alerta pelo limiar técnico"
    )
    return pd.DataFrame({
        "probabilidade_malignidade": probability,
        "limiar": limiar,
        "orientacao": triage,
        "aviso": CLINICAL_DISCLAIMER,
    }, index=amostras.index)


def run_full_analysis(file_bytes: bytes) -> TrainedAnalysis:
    """Executa o pipeline inteiro (equivalente a rodar o notebook do início ao fim).

    Quando o arquivo é compatível mas não tem amostras suficientes pra
    treinar (ver `check_trainable`), devolve uma `TrainedAnalysis` com
    `trainable=False` — validação e EDA preenchidas, modelagem/avaliação/
    explicabilidade vazias — em vez de lançar erro. Faltar dado pra treinar
    não é o mesmo que o arquivo estar errado.
    """
    data, y, X = load_and_validate(file_bytes)
    identificacao_csv = check_compatibility(data, X)
    eda = run_eda(data, X, y)

    trainable_issue = check_trainable(y)
    if trainable_issue is not None:
        return TrainedAnalysis(
            identificacao_csv=identificacao_csv,
            eda=eda,
            X_columns=X.columns.tolist(),
            X=X,
            y=y,
            trainable=False,
            trainable_issue=trainable_issue,
        )

    results_df, fitted_models, X_test, y_test = split_and_train(X, y)
    best_name = results_df.loc[0, "modelo"]
    best_model = fitted_models[best_name]

    analysis = TrainedAnalysis(
        identificacao_csv=identificacao_csv,
        eda=eda,
        results_df=results_df,
        fitted_models=fitted_models,
        best_name=best_name,
        best_model=best_model,
        X_columns=X.columns.tolist(),
        X=X,
        y=y,
        X_test=X_test,
        y_test=y_test,
    )
    analysis.evaluation = evaluate(best_model, X_test, y_test)
    analysis.explainability = explain(best_model, X_test, y_test)
    return analysis


def build_split_description(total_train: int, total_test: int) -> str:
    """Mesma frase dinâmica que a célula de geração do PDF do notebook escreve
    sobre a divisão treino/teste."""
    total = total_train + total_test
    if total == 0:
        return "A divisão entre treino e teste não foi executada nesta sessão."
    percentual_treino = (total_train / total) * 100
    percentual_teste = (total_test / total) * 100
    return (
        f"Nesta execução foram utilizadas {total_train} amostras para treino "
        f"({percentual_treino:.1f}%) e {total_test} amostras para teste "
        f"({percentual_teste:.1f}%)."
    )


def render_report_charts(
    assets_dir: Path,
    *,
    X: pd.DataFrame,
    y: pd.Series,
    best_model: Pipeline | None = None,
    X_test: pd.DataFrame | None = None,
    y_test: pd.Series | None = None,
    modelo_selecionado: str = "Modelo não treinado",
    importance_records: list[dict[str, Any]] | None = None,
) -> list[tuple[str, Path, str]]:
    """Gera os 4 gráficos do relatório em PDF (distribuição, correlação, matriz
    de confusão, importância) com o mesmo visual usado no notebook. Usada tanto
    pela célula 5.2 do notebook quanto pelo backend (`/api/report/pdf`), pra
    garantir que os dois produzam o mesmo PDF a partir dos mesmos dados.

    Devolve uma lista de ``(título, caminho_da_imagem, legenda)`` — o formato
    que ``scripts/generate_report_pdf.py`` espera para montar as páginas de
    gráficos. Pula um gráfico (em vez de falhar) quando faltam os dados que
    ele precisa — por exemplo, matriz de confusão sem modelo treinado.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import ConfusionMatrixDisplay

    assets_dir.mkdir(parents=True, exist_ok=True)
    graficos: list[tuple[str, Any, str]] = []

    # 1. Distribuição entre benignos e malignos
    caminho = assets_dir / "distribuicao_diagnosticos.png"
    plt.figure(figsize=(8, 5))
    sns.barplot(x=["Benigno", "Maligno"], y=[int((y == 0).sum()), int((y == 1).sum())], color="#1f77b4")
    plt.title("Distribuição dos diagnósticos")
    plt.xlabel("Diagnóstico")
    plt.ylabel("Quantidade de amostras")
    plt.tight_layout()
    plt.savefig(caminho, dpi=160)
    plt.close()
    graficos.append((
        "Distribuição dos diagnósticos",
        caminho,
        "O gráfico mostra a quantidade de casos benignos e malignos presentes na base.",
    ))

    # 2. Correlação com malignidade
    correlacoes = pd.concat([X, y.rename("maligno")], axis=1).corr(numeric_only=True)["maligno"].drop("maligno")
    top_atributos = correlacoes.abs().sort_values(ascending=False).head(10).index
    dados_correlacao = correlacoes.loc[top_atributos].sort_values()
    caminho = assets_dir / "correlacao_malignidade.png"
    plt.figure(figsize=(9, 6))
    sns.barplot(x=dados_correlacao.values, y=dados_correlacao.index, color="#b2182b")
    plt.title("Top 10 correlações com malignidade")
    plt.xlabel("Correlação de Pearson")
    plt.ylabel("Atributo")
    plt.tight_layout()
    plt.savefig(caminho, dpi=160)
    plt.close()
    graficos.append((
        "Correlação com malignidade",
        caminho,
        "A correlação mostra associação estatística com o diagnóstico, mas não demonstra causa clínica.",
    ))

    # 3. Matriz de confusão (só se houver modelo treinado)
    if best_model is not None and X_test is not None and y_test is not None:
        previsoes = best_model.predict(X_test)
        caminho = assets_dir / "matriz_confusao.png"
        fig, ax = plt.subplots(figsize=(6, 5))
        ConfusionMatrixDisplay.from_predictions(
            y_test, previsoes, display_labels=["Benigno", "Maligno"], cmap="Blues", ax=ax,
        )
        ax.set_title(f"Matriz de confusão — {modelo_selecionado}")
        plt.tight_layout()
        plt.savefig(caminho, dpi=160)
        plt.close()
        graficos.append((
            "Matriz de confusão",
            caminho,
            "A matriz mostra os acertos e erros do modelo, incluindo falsos positivos e falsos negativos.",
        ))

    # 4. Importância por permutação (só se houver)
    if importance_records:
        importance_df = pd.DataFrame(importance_records).sort_values("importancia_media")
        caminho = assets_dir / "importancia_atributos.png"
        plt.figure(figsize=(9, 6))
        sns.barplot(data=importance_df, x="importancia_media", y="atributo", color="#2166ac")
        plt.title("Importância dos atributos")
        plt.xlabel("Impacto médio no desempenho")
        plt.ylabel("Atributo")
        plt.tight_layout()
        plt.savefig(caminho, dpi=160)
        plt.close()
        graficos.append((
            "Importância por permutação",
            caminho,
            "Este gráfico mostra quais atributos mais impactaram o desempenho do modelo.",
        ))

    return graficos
