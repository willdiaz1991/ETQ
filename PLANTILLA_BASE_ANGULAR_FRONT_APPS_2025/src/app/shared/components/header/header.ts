import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Toolbar } from "primeng/toolbar";
import { Router } from '@angular/router';


@Component({
  selector: 'app-header',
  imports: [
    CommonModule,
    ButtonModule,
    FormsModule,
    ReactiveFormsModule,
    Toolbar
],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
   private readonly router =  inject(Router);

  //recibe data informacion para el ruteo
  goRoute(){
       // El listado de productos se sirve en la ruta raíz ('')
       this.router.navigate(['/']);
  }


}
