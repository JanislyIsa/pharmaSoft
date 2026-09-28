import { Routes } from '@angular/router';

export const CATEGORIAS_ROUTES: Routes = [
  { path: '', loadComponent: () => import('./pages/categoria-list/categoria-list').then((m) => m.CategoriaList), title: 'Categorías · PharmaSoft' },
  { path: 'nuevo', loadComponent: () => import('./pages/categoria-form/categoria-form').then((m) => m.CategoriaForm), title: 'Nueva categoría · PharmaSoft' },
  { path: ':id/editar', loadComponent: () => import('./pages/categoria-form/categoria-form').then((m) => m.CategoriaForm), title: 'Editar categoría · PharmaSoft' },
];
