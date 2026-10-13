import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PrintAuditRecord, PrintEtqResponse } from '../../core/models/printing.model';
import { PrintingApiService } from '../../core/services/printing-api.service';

@Component({
  selector: 'app-print-labels',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, ButtonModule, InputTextModule],
  templateUrl: './print-labels.html',
  styleUrl: './print-labels.scss',
})
export class PrintLabels {
  private readonly formBuilder = inject(FormBuilder);
  private readonly printingApi = inject(PrintingApiService);

  readonly printForm = this.formBuilder.nonNullable.group({
    lpn: ['olpn12345', [Validators.required, Validators.minLength(1)]],
    zone: ['ZONA-PICKING-A', Validators.required],
    requestedBy: ['usuario.operacion', Validators.required],
  });

  readonly result = signal<PrintEtqResponse | null>(null);
  readonly rejectionReasons = signal<string[]>([]);
  readonly history = signal<PrintAuditRecord[]>([]);
  readonly isSubmitting = signal(false);
  readonly isLoadingHistory = signal(false);
  readonly errorMessage = signal('');
  historyFilter = '';

  constructor() {
    this.loadHistory();
  }

  submitPrint(): void {
    if (this.printForm.invalid || this.isSubmitting()) {
      this.printForm.markAllAsTouched();
      return;
    }

    this.errorMessage.set('');
    this.result.set(null);
    this.rejectionReasons.set([]);
    this.isSubmitting.set(true);

    this.printingApi
      .print({
        request: { lpn: this.printForm.controls.lpn.value },
        zone: this.printForm.controls.zone.value,
        requestedBy: this.printForm.controls.requestedBy.value,
      })
      .pipe(finalize(() => this.isSubmitting.set(false)))
      .subscribe({
        next: (response) => {
          this.result.set(response);
          this.loadHistory();
        },
        error: (error: HttpErrorResponse) => {
          const reasons = this.getBusinessRejectionReasons(error);
          if (reasons) {
            this.rejectionReasons.set(reasons);
            this.loadHistory();
          } else {
            this.errorMessage.set(this.getHttpErrorMessage(error));
          }
        },
      });
  }

  loadHistory(): void {
    this.isLoadingHistory.set(true);
    this.printingApi
      .getHistory(this.historyFilter)
      .pipe(finalize(() => this.isLoadingHistory.set(false)))
      .subscribe({
        next: (response) => {
          if (response.result) {
            this.history.set(response.result);
          } else {
            this.errorMessage.set(response.errorMessage ?? 'La API no devolvió el historial.');
          }
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage.set(this.getHttpErrorMessage(error));
        },
      });
  }

  clearHistoryFilter(): void {
    this.historyFilter = '';
    this.loadHistory();
  }

  private getHttpErrorMessage(error: HttpErrorResponse): string {
    if (error.status === 0) {
      return 'No fue posible conectar con la API local. Verifica que FastAPI esté ejecutándose en http://127.0.0.1:8080.';
    }
    return error.error?.detail ?? error.message ?? 'Ocurrió un error al comunicarse con la API.';
  }

  private getBusinessRejectionReasons(error: HttpErrorResponse): string[] | null {
    const detail: unknown = error.error?.detail;
    if (error.status === 422 && Array.isArray(detail) && detail.every((reason) => typeof reason === 'string')) {
      return detail;
    }
    return null;
  }
}
