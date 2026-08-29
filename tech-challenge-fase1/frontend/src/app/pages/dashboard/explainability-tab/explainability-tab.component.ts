import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import { NgChartsModule } from 'ng2-charts';

import { AnalysisResponse } from '../../../core/models/analysis.model';
import { CHART_COLORS, darkScale } from '../../../core/chart-theme';

@Component({
  selector: 'app-explainability-tab',
  standalone: true,
  imports: [CommonModule, NgChartsModule],
  templateUrl: './explainability-tab.component.html',
})
export class ExplainabilityTabComponent implements OnChanges {
  @Input({ required: true }) analysis!: AnalysisResponse;

  permutationChartData: ChartData<'bar'> = { labels: [], datasets: [] };
  shapChartData: ChartData<'bar'> = { labels: [], datasets: [] };

  readonly horizontalBarOptions: ChartConfiguration<'bar'>['options'] = {
    indexAxis: 'y',
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: darkScale(), y: darkScale({ ticks: { color: '#8b96ad', font: { size: 10 } } }) },
  };

  ngOnChanges(): void {
    if (!this.analysis.trainable || !this.analysis.explainability.permutation_importance) {
      this.permutationChartData = { labels: [], datasets: [] };
      this.shapChartData = { labels: [], datasets: [] };
      return;
    }

    const permutation = [...this.analysis.explainability.permutation_importance].reverse();
    this.permutationChartData = {
      labels: permutation.map((item) => item.atributo),
      datasets: [
        {
          data: permutation.map((item) => item.importancia_media ?? 0),
          backgroundColor: CHART_COLORS.accent,
          borderRadius: 4,
        },
      ],
    };

    const shap = this.analysis.explainability.shap;
    if (shap) {
      const reversed = [...shap].reverse();
      this.shapChartData = {
        labels: reversed.map((item) => item.atributo),
        datasets: [
          {
            data: reversed.map((item) => item.impacto_medio_absoluto ?? 0),
            backgroundColor: CHART_COLORS.violet,
            borderRadius: 4,
          },
        ],
      };
    }
  }

  get hasShap(): boolean {
    return !!this.analysis.explainability.shap;
  }
}
