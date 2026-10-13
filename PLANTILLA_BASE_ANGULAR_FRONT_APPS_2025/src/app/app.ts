import { Component, effect, inject, OnInit, signal } from '@angular/core';
import { MenuItem, MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { RouterModule } from '@angular/router';
import { Footer } from './shared/components/footer/footer';
import { Header } from './shared/components/header/header';
import { CommonModule } from '@angular/common';
import { AvatarModule } from 'primeng/avatar';
import { Loading } from './shared/components/loading/loading';
import { ToastModule } from 'primeng/toast';
import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, Footer, Header, CommonModule, AvatarModule, ButtonModule, Loading, ToastModule],
  providers: [MessageService],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly messageService = inject(MessageService);

  items: MenuItem[] | undefined;
  home: MenuItem | undefined;

  protected readonly title = signal('etq-printing-web');

  /** Estado de autenticación expuesto por el AuthService (solo lectura). */
  protected readonly isAuthenticated = this.auth.isAuthenticated;
  protected readonly isLoading = this.auth.isLoading;

  constructor() {
    // Traduce las notificaciones del AuthService a toasts. Mantiene el servicio
    // agnóstico de UI y la responsabilidad de presentación en el componente.
    effect(() => {
      const notice = this.auth.notice();
      if (notice) {
        this.messageService.add(notice);
      }
    });
  }

  ngOnInit(): void {
    this.setupBreadcrumb();
    this.auth.init();
  }

  /** Configura el breadcrumb inicial. */
  private setupBreadcrumb(): void {
    this.items = [];
    this.home = {
      icon: 'pi pi-home',
      routerLink: '/home',
    };
  }
}
