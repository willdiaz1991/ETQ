import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  ApiResponse,
  PrintAuditRecord,
  PrintEtqResponse,
  PrintRequest,
} from '../models/printing.model';

@Injectable({ providedIn: 'root' })
export class PrintingApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = environment.printingApiBaseUrl.replace(/\/$/, '');

  print(request: PrintRequest): Observable<PrintEtqResponse> {
    return this.http.post<PrintEtqResponse>(`${this.apiBaseUrl}/printing/validate`, request);
  }

  getHistory(lpn?: string): Observable<ApiResponse<PrintAuditRecord[]>> {
    let params = new HttpParams();
    if (lpn?.trim()) {
      params = params.set('lpn', lpn.trim());
    }
    return this.http.get<ApiResponse<PrintAuditRecord[]>>(`${this.apiBaseUrl}/printing/history`, { params });
  }
}
