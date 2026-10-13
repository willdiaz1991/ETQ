import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

/**
 * Servicio centralizado para llamadas HTTP a la API del Hub.
 * Provee métodos genéricos y añade la subscription key de Azure API Management.
 *
 * Nota: el header `Authorization: Bearer <token>` lo añade automáticamente el
 * interceptor HTTP (única fuente de verdad para autenticación). Este servicio
 * NO debe establecerlo para evitar duplicación.
 */
@Injectable({
  providedIn: 'root'
})
export class DataService {
  private readonly http = inject(HttpClient);

  /**
   * Genera los headers propios de la API (subscription key).
   * El token de autenticación lo inyecta el interceptor.
   */
  protected generateBasicHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Ocp-Apim-Subscription-Key': environment.subscriptionKey
    });
  }

  /**
   * Valida el token actual contra la API de autenticación
   */
  authenticated(): Observable<any> {
    return this.http.get(environment.authenticated, {
      headers: this.generateBasicHeaders()
    });
  }

  /**
   * POST genérico a cualquier servicio
   */
  postGeneric(data: any, urlService: string): Observable<any> {
    return this.http.post(environment.api + urlService, data, {
      headers: this.generateBasicHeaders()
    });
  }

  /**
   * GET genérico a cualquier servicio
   */
  getGeneric(urlService: string): Observable<any> {
    return this.http.get(environment.api + urlService, {
      headers: this.generateBasicHeaders()
    });
  }
}
