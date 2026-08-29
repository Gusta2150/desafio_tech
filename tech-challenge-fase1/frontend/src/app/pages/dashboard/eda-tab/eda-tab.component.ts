import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import { NgChartsModule } from 'ng2-charts';

import { AnalysisResponse } from '../../../core/models/analysis.model';
import { CHART_COLORS, darkScale } from '../../../core/chart-theme';

@Component({
  selector: 'app-eda-tab',
  standalone: true,
  imports: [CommonModule, NgChartsModule],
  templateUrl: './eda-tab.component.html',
})
export class EdaTabComponent implements OnChanges {
  @Input({ required: true }) analysis!: AnalysisResponse;

  distributionChartData: ChartData<'bar'> = { labels: [], datasets: [] };
  correlationChartData: ChartData<'bar'> = { labels: [], datasets: [] };

  readonly barOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: darkScale(), y: darkScale() },
  };

  readonly horizontalBarOptions: ChartConfiguration<'bar'>['options'] = {
    indexAxis: 'y',
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: darkScale(), y: darkScale({ ticks: { color: '#8b96ad', font: { size: 10 } } }) },
  };

  ngOnChanges(): void {
    const distribution = this.analysis.eda.diagnosis_distribution;
    this.distributionChartData = {
      labels: ['Benigno', 'Maligno'],
      datasets: [
        {
          data: [distribution.Benigno, distribution.Maligno],
          backgroundColor: [CHART_COLORS.good, CHART_COLORS.critical],
          borderRadius: 6,
          maxBarThickness: 64,
        },
      ],
    };

    const entries = Object.entries(this.analysis.eda.top_correlations).sort(
      (a, b) => Math.abs(a[1]) - Math.abs(b[1])
    );
    this.correlationChartData = {
      labels: entries.map(([feature]) => feature),
      datasets: [
        {
          data: entries.map(([, value]) => value),
          backgroundColor: CHART_COLORS.accent,
          borderRadius: 4,
        },
      ],
    };
  }

  get featureNames(): string[] {
    return Object.keys(this.analysis.eda.describe);
  }

  describeRow(feature: string) {
    return this.analysis.eda.describe[feature];
  }
}
