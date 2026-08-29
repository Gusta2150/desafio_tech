import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { AnalysisResponse } from '../../../core/models/analysis.model';

@Component({
  selector: 'app-validation-tab',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './validation-tab.component.html',
})
export class ValidationTabComponent {
  @Input({ required: true }) analysis!: AnalysisResponse;

  get missingEntries(): [string, number][] {
    return Object.entries(this.analysis.eda.missing_values);
  }
}
