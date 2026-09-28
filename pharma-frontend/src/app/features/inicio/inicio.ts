import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-inicio',
  imports: [RouterLink],
  template: `
    <section class="welcome">
      <p class="eyebrow">PHARMASOFT · OPERACIONES</p>
      <h1>Tu botica, en orden.</h1>
      <p class="intro">Administra el catálogo y la información de tus clientes desde un solo lugar.</p>
      <div class="actions"><a class="button button-primary" routerLink="/clientes">Ver clientes <span>→</span></a><a class="button" routerLink="/categorias">Explorar categorías</a></div>
    </section>
    <section class="quick-grid" aria-label="Accesos rápidos">
      <a class="quick-card" routerLink="/categorias"><span class="quick-icon">▦</span><span><small>CATÁLOGO</small><strong>Categorías</strong><em>Organiza tus productos</em></span><b>↗</b></a>
      <a class="quick-card" routerLink="/clientes"><span class="quick-icon">♙</span><span><small>RELACIONES</small><strong>Clientes</strong><em>Consulta y actualiza registros</em></span><b>↗</b></a>
    </section>
    <p class="note"><span class="note-dot"></span> Conectado a PharmaBackend <code>localhost:8080</code></p>
  `,
  styles: [`
    .welcome { padding: clamp(27px, 5vw, 58px); border: 1px solid #e6ebe5; border-radius: 22px; background: linear-gradient(115deg,#fff 15%,#eef5f0 100%); }
    .eyebrow { margin: 0 0 18px; color: #548371; font-size: 10px; font-weight: 750; letter-spacing: .16em; }
    h1 { max-width: 640px; margin: 0; color: #183e35; font-size: clamp(38px, 6vw, 64px); line-height: 1.02; letter-spacing: -.06em; }
    .intro { max-width: 450px; margin: 18px 0 26px; color: #68766f; line-height: 1.7; font-size: 14px; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; }
    .button { display: inline-flex; gap: 18px; align-items: center; padding: 11px 15px; border: 1px solid #dbe3dd; border-radius: 10px; color: #315347; text-decoration: none; font-size: 12px; font-weight: 650; }
    .button-primary { border-color: #1c5848; background: #1c5848; color: #fff; }
    .quick-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 14px; margin-top: 18px; }
    .quick-card { display: flex; align-items: center; gap: 14px; padding: 19px; border: 1px solid #e6ebe5; border-radius: 15px; background: #fff; color: inherit; text-decoration: none; }
    .quick-card > span:nth-child(2) { display: grid; gap: 4px; }
    .quick-card small { color: #94a099; font-size: 9px; font-weight: 750; letter-spacing: .12em; }
    .quick-card strong { color: #26483d; font-size: 15px; }
    .quick-card em { color: #839087; font-size: 11px; font-style: normal; }
    .quick-card b { margin-left: auto; color: #719486; }
    .quick-icon { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 12px; background: #eef5f1; color: #356958; font-size: 20px; }
    .note { display: flex; align-items: center; gap: 8px; margin: 21px 3px; color: #77837c; font-size: 11px; }
    .note-dot { width: 7px; height: 7px; border-radius: 50%; background: #53a179; }
    code { color: #52675c; }
    @media(max-width:600px) { .quick-grid { grid-template-columns: 1fr; } }
  `],
})
export class Inicio {}
