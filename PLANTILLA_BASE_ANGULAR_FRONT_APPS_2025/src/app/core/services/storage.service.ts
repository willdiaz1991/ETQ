import { Injectable } from '@angular/core';

/**
 * Servicio para almacenar estado global en memoria
 * Usado para compartir datos entre componentes sin necesidad de observables
 */
@Injectable({
  providedIn: 'root'
})
export class StorageService {
  private _json: any = null;
  private _userLogged = '';

  /**
   * Almacena datos JSON genéricos
   */
  get json(): any {
    return this._json;
  }

  set json(value: any) {
    this._json = value;
  }

  /**
   * Usuario logueado actualmente
   */
  get userLogged(): string {
    return this._userLogged;
  }

  set userLogged(value: string) {
    this._userLogged = value;
  }
}
