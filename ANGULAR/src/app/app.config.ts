import { ApplicationConfig, LOCALE_ID, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { DialogService } from 'primeng/dynamicdialog';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { Interceptors } from './interceptors/interceptor';
  /**
   *configuracion de estilos de proyecto
   */

export const appConfig: ApplicationConfig = {
  providers: [
     { provide: LOCALE_ID, useValue: 'es-CO' },
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes),
    provideHttpClient(
        withInterceptors([Interceptors])
    ),
    provideAnimationsAsync(),
    providePrimeNG({
      theme:{
        preset:Aura,
         options: {
          prefix: 'p',
          scale: 0.9,
          darkModeSelector: false
        },
      },
      ripple: true
    }),
 DialogService
  ]
};
