import { environment } from '../../../environments/environment';

export class Constants {
  /**
   * Clave para encriptación AES cargada en runtime por el contenedor
   * (se recibe vía postMessage y se guarda en sessionStorage).
   */
  static get cryptoHelper(): string {
    return sessionStorage.getItem('cryptoKey') || '';
  }

  /**
   * Versión de la aplicación (fuente única: environment).
   */
  static readonly appVersion = environment.version;

  /**
   * Nombre del ambiente (fuente única: environment).
   */
  static readonly environmentName = environment.environmentName;
}
