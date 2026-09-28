import { Routes } from '@angular/router';

export const CLIENTES_ROUTES: Routes = [
  { path: '', loadComponent: () => import('./pages/cliente-list/cliente-list').then((m) => m.ClienteList), title: 'Clientes · PharmaSoft' },
  { path: 'nuevo', loadComponent: () => import('./pages/cliente-form/cliente-form').then((m) => m.ClienteForm), title: 'Nuevo cliente · PharmaSoft' },
  { path: ':id/editar', loadComponent: () => import('./pages/cliente-form/cliente-form').then((m) => m.ClienteForm), title: 'Editar cliente · PharmaSoft' },
];
