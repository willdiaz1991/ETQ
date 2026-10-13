import { DestroyRef, Injectable, inject, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import { DataService } from './data.service';
import { StorageService } from './storage.service';

/**
 * Notificación de estado de autenticación. El AuthService es agnóstico de UI:
 * solo expone qué comunicar; la capa de presentación decide cómo mostrarlo
 * (toast, banner, etc.).
 */
export interface AuthNotice {
  severity: 'success' | 'info' | 'warn' | 'error';
  summary: string;
  detail: string;
}

/** Estructura del mensaje que envía la aplicación contenedora. */
interface ContainerMessage {
  type?: string;
  token?: string;
  user?: string;
  cryptoKey?: string;
  taskFind?: { idTarea?: string | number;[key: string]: unknown };
}

/**
 * Orquesta la autenticación del micro-front: recibe la sesión de la aplicación
 * contenedora vía `postMessage`, valida el origen, persiste la sesión y valida
 * el token contra el backend (en producción).
 *
 * Expone el estado mediante señales de solo lectura para que el componente raíz
 * se mantenga delgado y testeable.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly dataService = inject(DataService);
  private readonly storage = inject(StorageService);
  private readonly destroyRef = inject(DestroyRef);

  /** Tipo de mensaje del handshake. Debe coincidir con el de la contenedora. */
  private static readonly READY_SIGNAL = 'MICROFRONTAL_READY';

  /** Espera antes de activar la sesión de desarrollo cuando no llega token. */
  private static readonly DEV_FALLBACK_MS = 3000;

  private readonly _isAuthenticated = signal(false);
  private readonly _isLoading = signal(true);
  private readonly _notice = signal<AuthNotice | null>(null);

  /** `true` cuando hay una sesión válida. */
  readonly isAuthenticated = this._isAuthenticated.asReadonly();
  /** `true` mientras se resuelve la autenticación inicial. */
  readonly isLoading = this._isLoading.asReadonly();
  /** Último mensaje a comunicar al usuario (lo traduce la UI). */
  readonly notice = this._notice.asReadonly();

  private initialized = false;

  /**
   * Inicia el flujo de autenticación. Idempotente: invocarlo varias veces no
   * registra listeners duplicados.
   */
  init(): void {
    if (this.initialized) return;
    this.initialized = true;

    // 1. Registrar el listener ANTES de cualquier otra cosa para no perder el
    //    mensaje de la contenedora por una race condition de carga del iframe.
    window.addEventListener('message', this.onContainerMessage);
    this.destroyRef.onDestroy(() =>
      window.removeEventListener('message', this.onContainerMessage),
    );

    // 2. Handshake: avisar a la contenedora que ya estamos listos para el token.
    this.notifyContainerReady();

    // 3. Modo desarrollo: si no llega token, iniciar sesión de prueba.
    if (environment.allowDevAccess) {
      this.scheduleDevFallback();
    }
  }

  /** Handler de mensajes de la contenedora (arrow para conservar `this`). */
  private readonly onContainerMessage = (event: MessageEvent): void => {
    // Ignora el propio origen (ruido del navegador / eco del handshake).
    if (event.origin === window.origin) return;

    if (!this.isAllowedOrigin(event.origin)) {
      this.fail('Esta aplicación solo puede ser accedida desde dominios autorizados');
      return;
    }

    const data = event.data as ContainerMessage | null;
    if (!data || typeof data !== 'object') return;
    if (data.type === AuthService.READY_SIGNAL) return; // eco del handshake
    if (!data.token) return;

    // Evita reprocesar la misma sesión ya activa.
    if (sessionStorage.getItem('token') === data.token && this._isAuthenticated()) {
      return;
    }

    this.storeSession(data);
    this.validateToken();
  };

  /** Persiste los datos de sesión recibidos de la contenedora. */
  private storeSession(data: ContainerMessage): void {
    sessionStorage.setItem('token', data.token as string);

    if (data.cryptoKey) {
      sessionStorage.setItem('cryptoKey', data.cryptoKey);
    }

    this.storage.userLogged = data.user ?? '';

    if (data.taskFind) {
      if (data.taskFind.idTarea != null) {
        sessionStorage.setItem('TaskId', String(data.taskFind.idTarea));
      }
      sessionStorage.setItem('Task', JSON.stringify(data.taskFind));
    }
  }

  /** Valida el token: simulado fuera de producción, real contra el backend en PROD. */
  private validateToken(): void {
    if (!environment.production) {
      this.markAuthenticated({
        severity: 'info',
        summary: 'Modo Desarrollo',
        detail: 'Autenticación simulada - token no validado contra API',
      });
      return;
    }

    this.dataService.authenticated().subscribe({
      next: () =>
        this.markAuthenticated({
          severity: 'success',
          summary: 'Autenticado',
          detail: 'Sesión iniciada correctamente',
        }),
      error: () => this.fail('Token inválido o expirado'),
    });
  }

  /** Modo desarrollo: inicia una sesión de prueba si no llegó token. */
  private scheduleDevFallback(): void {
    setTimeout(() => {
      if (this._isAuthenticated()) return;
      this.storage.userLogged = 'USUARIO_TEST';
      this.markAuthenticated({
        severity: 'warn',
        summary: 'Acceso Desarrollo',
        detail: 'Sesión iniciada sin token - solo para desarrollo',
      });
    }, AuthService.DEV_FALLBACK_MS);
  }

  private markAuthenticated(notice: AuthNotice): void {
    this._isAuthenticated.set(true);
    this._isLoading.set(false);
    this._notice.set(notice);
  }

  private fail(detail: string): void {
    sessionStorage.clear();
    this._isAuthenticated.set(false);
    this._isLoading.set(false);
    this._notice.set({ severity: 'error', summary: 'Error de autenticación', detail });
  }

  /**
   * Handshake hacia la contenedora. Resuelve un `targetOrigin` concreto para no
   * difundir a `'*'`; el mensaje no contiene datos sensibles.
   */
  private notifyContainerReady(): void {
    if (window.parent === window) return; // no estamos embebidos
    window.parent.postMessage({ type: AuthService.READY_SIGNAL }, this.resolveParentOrigin());
  }

  /** Determina el origen del marco padre de la forma más fiable disponible. */
  private resolveParentOrigin(): string {
    try {
      if (document.referrer) return new URL(document.referrer).origin;
    } catch {
      /* referrer no parseable */
    }

    const ancestors = window.location.ancestorOrigins;
    if (ancestors && ancestors.length > 0) return ancestors[0];

    // Sin forma de resolverlo; el ping de readiness no lleva datos sensibles.
    return '*';
  }

  /**
   * Valida el origen del mensaje contra `environment.allowedParentOrigins`
   * (sufijos de host). En no-producción se permite `localhost`.
   */
  private isAllowedOrigin(origin: string): boolean {
    let hostname = '';
    try {
      hostname = new URL(origin).hostname.toLowerCase();
    } catch {
      return false;
    }

    if (!environment.production && hostname === 'localhost') return true;

    return (environment.allowedParentOrigins ?? []).some((suffix) => {
      const normalized = suffix.toLowerCase();
      return hostname === normalized || hostname.endsWith(normalized);
    });
  }
}
