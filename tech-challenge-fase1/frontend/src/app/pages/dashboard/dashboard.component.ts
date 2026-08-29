import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AnalysisService } from '../../core/services/analysis.service';
import { AnalysisResponse } from '../../core/models/analysis.model';
import { ClinicalDisclaimerComponent } from '../../shared/clinical-disclaimer/clinical-disclaimer.component';
import { TopBarComponent } from '../../shared/top-bar/top-bar.component';
import { ValidationTabComponent } from './validation-tab/validation-tab.component';
import { EdaTabComponent } from './eda-tab/eda-tab.component';
import { ModelingTabComponent } from './modeling-tab/modeling-tab.component';
import { EvaluationTabComponent } from './evaluation-tab/evaluation-tab.component';
import { ExplainabilityTabComponent } from './explainability-tab/explainability-tab.component';
import { PredictTabComponent } from './predict-tab/predict-tab.component';

type TabId = 'validation' | 'eda' | 'modeling' | 'evaluation' | 'explainability' | 'predict';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    ClinicalDisclaimerComponent,
    TopBarComponent,
    ValidationTabComponent,
    EdaTabComponent,
    ModelingTabComponent,
    EvaluationTabComponent,
    ExplainabilityTabComponent,
    PredictTabComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  analysis: AnalysisResponse | null = null;
  activeTab: TabId = 'validation';

  readonly tabs: { id: TabId; label: string }[] = [
    { id: 'validation', label: '1. Validação' },
    { id: 'eda', label: '2. EDA' },
    { id: 'modeling', label: '3. Modelagem' },
    { id: 'evaluation', label: '4. Avaliação' },
    { id: 'explainability', label: '5. Explicabilidade' },
    { id: 'predict', label: '6. Prever amostra' },
  ];

  constructor(
    private readonly analysisService: AnalysisService,
    private readonly router: Router
  ) {}

  ngOnInit(): void {
    this.analysis = this.analysisService.currentAnalysis;
    if (!this.analysis) {
      this.router.navigate(['/upload']);
      return;
    }
  }

  selectTab(tab: TabId): void {
    this.activeTab = tab;
  }

  startOver(): void {
    this.analysisService.clear();
    this.router.navigate(['/upload']);
  }
}
