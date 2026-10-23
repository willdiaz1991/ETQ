import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Footer } from './shared/components/footer/footer';
import { Header } from './shared/components/header/header';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, Footer, Header],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
}
