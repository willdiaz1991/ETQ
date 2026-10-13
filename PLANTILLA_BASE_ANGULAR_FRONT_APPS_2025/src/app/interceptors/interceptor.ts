import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../environments/environment';

/**
 * Bases de URL consideradas "propias" (API del Hub). El token de sesión solo
 * se adjunta a peticiones dirigidas a estos destinos para evitar filtrar el
 * bearer token a dominios de terceros o a assets estáticos (p. ej. products.json).
 */
const API_BASES = [environment.api, environment.authenticated].filter(Boolean);

function isOwnApi(url: string): boolean {
  return API_BASES.some((base) => url.startsWith(base));
}

/**
 * Interceptor HTTP que añade el token de autenticación a las peticiones
 * dirigidas a la API del Hub.
 *
 * Es la **única fuente** del header `Authorization` en la aplicación: los
 * servicios (p. ej. `DataService`) no deben volver a establecerlo.
 *
 * Reglas:
 * - Solo adjunta `Authorization` a URLs de la propia API (`API_BASES`) y cuando
 *   existe un token en sessionStorage (evita enviar `Bearer ` vacío).
 * - No sobreescribe `Content-Type` si la petición ya lo define o si el cuerpo
 *   es `FormData` (multipart), donde el navegador establece el boundary.
 */
export const Interceptors: HttpInterceptorFn = (req, next) => {
  let headers = req.headers;

  const token = sessionStorage.getItem('token');
  if (token && isOwnApi(req.url)) {
    headers = headers.set('Authorization', `Bearer ${token}`);
  }

  const isFormData = req.body instanceof FormData;
  if (!isFormData && !headers.has('Content-Type')) {
    headers = headers.set('Content-Type', 'application/json');
  }

  return next(req.clone({ headers }));
};
