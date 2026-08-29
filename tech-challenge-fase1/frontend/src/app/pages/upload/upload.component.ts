import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { ClinicalDisclaimerComponent } from '../../shared/clinical-disclaimer/clinical-disclaimer.component';
import { TopBarComponent } from '../../shared/top-bar/top-bar.component';
import { ApiErrorDetail } from '../../core/models/analysis.model';
import { AnalysisService, IncompatibleInputError } from '../../core/services/analysis.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, ClinicalDisclaimerComponent, TopBarComponent],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss'],
})
export class UploadComponent {
  selectedFile: File | null = null;
  isDragging = false;
  loading = false;

  /** Falha técnica (rede, servidor fora do ar etc.) — algo deu errado de verdade. */
  errorMessage: string | null = null;

  /** Resultado esperado: o CSV enviado não é do domínio de câncer de mama. */
  incompatible: ApiErrorDetail | null = null;

  constructor(
    private readonly analysisService: AnalysisService,
    private readonly router: Router
  ) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.setFile(input.files?.[0] ?? null);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    if (!this.loading) {
      this.isDragging = true;
    }
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  onDrop(event: DragEvent, fileInput: HTMLInputElement): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
    if (this.loading) {
      return;
    }

    const file = event.dataTransfer?.files?.[0] ?? null;
    if (file && !file.name.toLowerCase().endsWith('.csv')) {
      this.errorMessage = 'Apenas arquivos .csv são aceitos.';
      return;
    }

    // Sincroniza o <input type="file"> nativo para manter os dois em conjunto.
    if (file) {
      const transfer = new DataTransfer();
      transfer.items.add(file);
      fileInput.files = transfer.files;
    }
    this.setFile(file);
  }

  clearFile(fileInput: HTMLInputElement): void {
    fileInput.value = '';
    this.setFile(null);
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) {
      return `${bytes} B`;
    }
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  runWithUploadedFile(): void {
    if (!this.selectedFile) {
      this.errorMessage = 'Selecione um arquivo CSV antes de continuar.';
      return;
    }
    this.run(this.selectedFile);
  }

  runWithDefaultDataset(): void {
    this.run(null);
  }

  private setFile(file: File | null): void {
    this.selectedFile = file;
    this.errorMessage = null;
    this.incompatible = null;
  }

  private run(file: File | null): void {
    this.loading = true;
    this.errorMessage = null;
    this.incompatible = null;

    this.analysisService.runAnalysis(file).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (error: Error) => {
        this.loading = false;
        if (error instanceof IncompatibleInputError) {
          this.incompatible = error.detail;
        } else {
          this.errorMessage = error.message;
        }
      },
    });
  }
}
