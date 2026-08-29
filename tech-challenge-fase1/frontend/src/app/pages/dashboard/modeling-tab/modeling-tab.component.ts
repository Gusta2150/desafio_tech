import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { AnalysisResponse } from '../../../core/models/analysis.model';

@Component({
  selector: 'app-modeling-tab',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './modeling-tab.component.html',
})
export class ModelingTabComponent {
  @Input({ required: true }) analysis!: AnalysisResponse;
}
