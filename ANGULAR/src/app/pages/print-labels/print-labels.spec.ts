import { HttpErrorResponse } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { PrintAuditRecord, PrintEtqResponse } from '../../core/models/printing.model';
import { PrintingApiService } from '../../core/services/printing-api.service';
import { PrintLabels } from './print-labels';

describe('PrintLabels', () => {
  let fixture: ComponentFixture<PrintLabels>;
  let component: PrintLabels;
  let printingApi: jasmine.SpyObj<PrintingApiService>;

  const printResponse: PrintEtqResponse = {
    response: {
      idEtiqueta: '12345',
      purchaseOrder: 'PO123456',
      tcOrderId: 'TC78910',
      sku: 'SKU001',
      unidades: 25,
      zpl: '^XA^XZ',
    },
  };

  const auditRecord: PrintAuditRecord = {
    requestId: 'request-1',
    requestedAt: '2026-10-23T12:00:00Z',
    approved: true,
    lpn: 'olpn12345',
    etqId: '12345',
    zone: 'ZONA-PICKING-A',
    requestedBy: 'usuario.operacion',
    eventType: 'PRINT',
    isReprint: false,
    reasons: [],
  };

  beforeEach(async () => {
    printingApi = jasmine.createSpyObj<PrintingApiService>('PrintingApiService', ['print', 'getHistory']);
    printingApi.getHistory.and.returnValue(
      of({
        errorMessage: null,
        isError: false,
        isSuccessful: true,
        messages: null,
        result: [auditRecord],
      }),
    );

    await TestBed.configureTestingModule({
      imports: [PrintLabels],
      providers: [{ provide: PrintingApiService, useValue: printingApi }],
    }).compileComponents();

    fixture = TestBed.createComponent(PrintLabels);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('loads and renders print history on startup', () => {
    expect(printingApi.getHistory).toHaveBeenCalledOnceWith('');
    expect(fixture.nativeElement.textContent).toContain('Historial de impresiones');
    expect(fixture.nativeElement.textContent).toContain('olpn12345');
  });

  it('does not submit an invalid form and marks its fields as touched', () => {
    component.printForm.controls.lpn.setValue('');

    component.submitPrint();

    expect(printingApi.print).not.toHaveBeenCalled();
    expect(component.printForm.controls.lpn.touched).toBeTrue();
  });

  it('submits the request, displays the result and refreshes history', () => {
    printingApi.print.and.returnValue(of(printResponse));

    component.submitPrint();
    fixture.detectChanges();

    expect(printingApi.print).toHaveBeenCalledOnceWith({
      request: { lpn: 'olpn12345' },
      zone: 'ZONA-PICKING-A',
      requestedBy: 'usuario.operacion',
    });
    expect(component.result()).toEqual(printResponse);
    expect(printingApi.getHistory).toHaveBeenCalledTimes(2);
    expect(fixture.nativeElement.textContent).toContain('Impresión autorizada');
  });

  it('shows business rejection reasons and refreshes history', () => {
    const rejectionReason = 'El documento origen está anulado o devuelto.';
    printingApi.print.and.returnValue(
      throwError(() => new HttpErrorResponse({ status: 422, error: { detail: [rejectionReason] } })),
    );

    component.submitPrint();
    fixture.detectChanges();

    expect(component.rejectionReasons()).toEqual([rejectionReason]);
    expect(printingApi.getHistory).toHaveBeenCalledTimes(2);
    expect(fixture.nativeElement.textContent).toContain(rejectionReason);
  });

  it('shows a connection message for transport errors', () => {
    printingApi.print.and.returnValue(throwError(() => new HttpErrorResponse({ status: 0 })));

    component.submitPrint();

    expect(component.errorMessage()).toContain('No fue posible conectar con la API local');
    expect(printingApi.getHistory).toHaveBeenCalledTimes(1);
  });
});
