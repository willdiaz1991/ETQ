import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

/**
 * Objeto para manejar información del header/breadcrumb de la página
 */
export class HeaderObj {
  tittleName: string;
  routePath: string;
  backButton: boolean;

  constructor(tittleName: string, routePath = '', backButton = false) {
    this.tittleName = tittleName;
    this.routePath = routePath;
    this.backButton = backButton;
  }
}

/**
 * Servicio para gestionar breadcrumbs y headers de página
 * Permite actualizar el título y rutas desde cualquier componente
 */
@Injectable({
  providedIn: 'root'
})
export class PageService {
  private readonly headerPageVar = new BehaviorSubject(new HeaderObj(''));

  /**
   * Observable del header actual.
   * Los componentes deben suscribirse con el pipe `async` para que la
   * detección de cambios (zoneless) reaccione automáticamente.
   */
  get headerPage(): BehaviorSubject<HeaderObj> {
    return this.headerPageVar;
  }

  /**
   * Actualiza el header de la página.
   */
  setHeaderPage(value: HeaderObj): void {
    this.headerPageVar.next(value);
  }
}