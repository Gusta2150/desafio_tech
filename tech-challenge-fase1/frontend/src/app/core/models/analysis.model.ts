/**
 * Tipagem espelhando `backend/app/schemas.py` e `src/pipeline.py`.
 * Mantenha os dois lados em sincronia ao alterar o contrato da API.
 */

export interface IdentificacaoCsv {
  status: string;
  dominio_identificado: string;
  mensagem: string;
  amostras?: number;
  atributos?: number;
}

export interface DescribeStats {
  count: number;
  mean: number;
  std: number;
  min: number;
  '25%': number;
  '50%': number;
  '75%': number;
  max: number;
}

export interface EdaResult {
  describe: Record<string, DescribeStats>;
  missing_values: Record<string, number>;
  diagnosis_distribution: { Benigno: number; Maligno: number };
  top_correlations: Record<string, number>;
  correlation_matrix_top_features: Record<string, Record<string, number>>;
}

export interface ModelComparisonRow {
  modelo: string;
  accuracy: number;
  recall_maligno: number;
  f1_maligno: number;
  roc_auc: number;
}

export interface ClassMetrics {
  precision: number;
  recall: number;
  'f1-score': number;
  support: number;
}

export interface ClassificationReport {
  Benigno: ClassMetrics;
  Maligno: ClassMetrics;
  accuracy: number;
  'macro avg': ClassMetrics;
  'weighted avg': ClassMetrics;
}

export interface RocPoint {
  fpr: number;
  tpr: number;
}

export interface EvaluationResult {
  classification_report: ClassificationReport;
  confusion_matrix: { labels: string[]; matrix: number[][] };
  roc_curve: RocPoint[];
  roc_auc: number;
}

export interface FeatureImportance {
  atributo: string;
  importancia_media?: number;
  desvio_padrao?: number;
  impacto_medio_absoluto?: number;
}

export interface ExplainabilityResult {
  permutation_importance: FeatureImportance[];
  shap: FeatureImportance[] | null;
  shap_error: string | null;
}

/** Motivo pelo qual não foi possível treinar um modelo novo com o arquivo enviado. */
export interface TrainableIssue {
  status: string;
  mensagem: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  identificacao_csv: IdentificacaoCsv;
  eda: EdaResult;
  models_comparison: ModelComparisonRow[];
  /** `null` quando `trainable` é `false` — nenhum modelo foi treinado. */
  best_model: string | null;
  /** Populado apenas quando `trainable` é `true`. */
  evaluation: Partial<EvaluationResult>;
  /** Populado apenas quando `trainable` é `true`. */
  explainability: Partial<ExplainabilityResult>;
  feature_names: string[];
  /** `false` = arquivo válido, mas sem amostras suficientes pra treinar (ver `trainable_issue`). */
  trainable: boolean;
  trainable_issue: TrainableIssue | null;
}

export interface PredictionResult {
  probabilidade_malignidade: number;
  limiar: number;
  orientacao: string;
  aviso: string;
}

export interface PredictResponse {
  predictions: PredictionResult[];
}

/** Corpo de erro devolvido pela API quando o CSV/amostra é incompatível (HTTP 422). */
export interface ApiErrorDetail {
  status: string;
  mensagem: string;
  dominio_identificado?: string;
  campos_ausentes?: string[];
  colunas_ausentes?: string[];
}
