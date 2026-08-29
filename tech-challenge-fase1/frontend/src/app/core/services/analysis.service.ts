import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, catchError, tap, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AnalysisResponse,
  ApiErrorDetail,
  PredictResponse,
} from '../models/analysis.model';

export interface PredictRequestBody {
  analysis_id: string;
  samples: Record<string, number>[];
  limiar?: number;
}

/**
 * Erro de validação "esperado" da API (HTTP 422) — o CSV/amostra não é
 * compatível com o domínio de câncer de mama. Carrega o detalhe estruturado
 * (`status`, `dominio_identificado`, `campos_ausentes`...) para a UI mostrar
 * um resultado informativo, não uma mensagem de falha genérica.
 */
export class IncompatibleInputError extends Error {
  constructor(readonly detail: ApiErrorDetail) {
    super(detail.mensagem);
    this.name = 'IncompatibleInputError';
  }
}

@Injectable({ providedIn: 'root' })
export class AnalysisService {
  private readonly baseUrl = environment.apiBaseUrl;

  /** Última análise carregada, compartilhada entre as abas do dashboard. */
  private readonly analysisSubject = new BehaviorSubject<AnalysisResponse | null>(null);
  readonly analysis$ = this.analysisSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  get currentAnalysis(): AnalysisResponse | null {
    return this.analysisSubject.value;
  }

  /** Faz upload de um CSV e roda o pipeline completo. Sem `file`, usa o dataset padrão do backend. */
  runAnalysis(file: File | null): Observable<AnalysisResponse> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }

    return this.http.post<AnalysisResponse>(`${this.baseUrl}/analysis`, formData).pipe(
      tap((result) => this.analysisSubject.next(result)),
      catchError((error) => this.rethrowWithDetail(error))
    );
  }

  predict(body: PredictRequestBody): Observable<PredictResponse> {
    return this.http
      .post<PredictResponse>(`${this.baseUrl}/predict`, body)
      .pipe(catchError((error) => this.rethrowWithDetail(error)));
  }

  downloadReportPdf(analysisId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/report/pdf`, {
      params: { analysis_id: analysisId },
      responseType: 'blob',
    });
  }

  clear(): void {
    this.analysisSubject.next(null);
  }

  private rethrowWithDetail(error: HttpErrorResponse) {
    const detail = error.error?.detail as ApiErrorDetail | string | undefined;

    // HTTP 422 com um objeto de detalhe = validação "esperada" (CSV de outro
    // domínio, rótulos inválidos etc.), não uma falha técnica.
    if (error.status === 422 && detail && typeof detail === 'object') {
      return throwError(() => new IncompatibleInputError(detail));
    }

    const message =
      typeof detail === 'string'
        ? detail
        : detail?.mensagem ?? 'Não foi possível completar a operação. Tente novamente.';
    return throwError(() => new Error(message));
  }
}
