import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { AnalysisResponse, PredictionResult } from '../../../core/models/analysis.model';
import { AnalysisService } from '../../../core/services/analysis.service';

interface BatchRow {
  index: number;
  result?: PredictionResult;
  error?: string;
}

@Component({
  selector: 'app-predict-tab',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './predict-tab.component.html',
})
export class PredictTabComponent implements OnChanges {
  @Input({ required: true }) analysis!: AnalysisResponse;

  manualForm: FormGroup = this.fb.group({});
  manualLoading = false;
  manualError: string | null = null;
  manualResult: PredictionResult | null = null;

  batchLoading = false;
  batchError: string | null = null;
  batchResults: BatchRow[] = [];
  batchFileName: string | null = null;

  pdfLoading = false;
  pdfError: string | null = null;

  constructor(private readonly fb: FormBuilder, private readonly analysisService: AnalysisService) {}

  ngOnChanges(): void {
    const controls: Record<string, unknown> = {};
    for (const feature of this.analysis.feature_names) {
      const mean = this.analysis.eda.describe[feature]?.mean ?? 0;
      controls[feature] = [mean, [Validators.required]];
    }
    this.manualForm = this.fb.group(controls);
  }

  submitManual(): void {
    if (this.manualForm.invalid) {
      this.manualForm.markAllAsTouched();
      return;
    }

    this.manualLoading = true;
    this.manualError = null;
    this.manualResult = null;

    this.analysisService
      .predict({
        analysis_id: this.analysis.analysis_id,
        samples: [this.manualForm.value],
      })
      .subscribe({
        next: (response) => {
          this.manualLoading = false;
          this.manualResult = response.predictions[0];
        },
        error: (error: Error) => {
          this.manualLoading = false;
          this.manualError = error.message;
        },
      });
  }

  onBatchFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }
    this.batchFileName = file.name;
    this.batchError = null;
    this.batchResults = [];

    const reader = new FileReader();
    reader.onload = () => this.runBatch(String(reader.result ?? ''));
    reader.onerror = () => (this.batchError = 'Não foi possível ler o arquivo.');
    reader.readAsText(file);
  }

  private runBatch(csvText: string): void {
    const rows = this.parseCsv(csvText);
    if (rows.length === 0) {
      this.batchError = 'CSV vazio ou em formato inválido.';
      return;
    }

    this.batchLoading = true;
    this.analysisService
      .predict({ analysis_id: this.analysis.analysis_id, samples: rows })
      .subscribe({
        next: (response) => {
          this.batchLoading = false;
          this.batchResults = response.predictions.map((result, index) => ({ index, result }));
        },
        error: (error: Error) => {
          this.batchLoading = false;
          this.batchError = error.message;
        },
      });
  }

  /** Parser simples de CSV: sem suporte a vírgulas dentro de aspas (suficiente pro dataset numérico do projeto). */
  private parseCsv(csvText: string): Record<string, number>[] {
    const lines = csvText.split(/\r?\n/).filter((line) => line.trim().length > 0);
    if (lines.length < 2) {
      return [];
    }
    const headers = lines[0].split(',').map((header) => header.trim());
    return lines.slice(1).map((line) => {
      const values = line.split(',');
      const row: Record<string, number> = {};
      headers.forEach((header, index) => {
        const parsed = Number(values[index]);
        if (!Number.isNaN(parsed)) {
          row[header] = parsed;
        }
      });
      return row;
    });
  }

  downloadPdf(): void {
    this.pdfLoading = true;
    this.pdfError = null;

    this.analysisService.downloadReportPdf(this.analysis.analysis_id).subscribe({
      next: (blob) => {
        this.pdfLoading = false;
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'analise_diagnostica_cancer_mama.pdf';
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error: Error) => {
        this.pdfLoading = false;
        this.pdfError = error.message;
      },
    });
  }

  triageClass(result: PredictionResult | undefined): string {
    if (!result) {
      return '';
    }
    return result.orientacao.startsWith('Encaminhar') ? 'badge--danger' : 'badge--ok';
  }
}
