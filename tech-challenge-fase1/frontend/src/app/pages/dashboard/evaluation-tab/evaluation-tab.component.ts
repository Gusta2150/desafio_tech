import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import { NgChartsModule } from 'ng2-charts';

import { AnalysisResponse } from '../../../core/models/analysis.model';
import { CHART_COLORS, darkScale } from '../../../core/chart-theme';

@Component({
  selector: 'app-evaluation-tab',
  standalone: true,
  imports: [CommonModule, NgChartsModule],
  templateUrl: './evaluation-tab.component.html',
})
export class EvaluationTabComponent implements OnChanges {
  @Input({ required: true }) analysis!: AnalysisResponse;

  rocChartData: ChartData<'line', { x: number; y: number }[]> = { datasets: [] };

  readonly rocOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    parsing: false,
    scales: {
      x: darkScale({
        type: 'linear',
        title: { display: true, text: 'Falso positivo (FPR)', color: '#8b96ad' },
        min: 0,
        max: 1,
      }),
      y: darkScale({
        title: { display: true, text: 'Verdadeiro positivo (TPR)', color: '#8b96ad' },
        min: 0,
        max: 1,
      }),
    },
    plugins: { legend: { display: false } },
    elements: { point: { radius: 0 } },
  };

  ngOnChanges(): void {
    const points = this.analysis.evaluation.roc_curve;
    if (!this.analysis.trainable || !points) {
      this.rocChartData = { datasets: [] };
      return;
    }
    this.rocChartData = {
      datasets: [
        {
          label: 'Modelo',
          data: points.map((p) => ({ x: p.fpr, y: p.tpr })),
          borderColor: CHART_COLORS.accent,
          backgroundColor: CHART_COLORS.accentSoft,
          borderWidth: 2,
          fill: true,
          tension: 0.15,
          pointRadius: 0,
        },
        {
          label: 'Aleatório (referência)',
          data: [
            { x: 0, y: 0 },
            { x: 1, y: 1 },
          ],
          borderColor: '#4b5875',
          borderDash: [6, 6],
          borderWidth: 1.5,
          fill: false,
          pointRadius: 0,
        },
      ],
    };
  }

  get confusionLabels(): string[] {
    return this.analysis.evaluation.confusion_matrix?.labels ?? [];
  }

  get confusionMatrix(): number[][] {
    return this.analysis.evaluation.confusion_matrix?.matrix ?? [];
  }
}
