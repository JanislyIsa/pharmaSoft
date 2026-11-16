"""Informe breve S14: evidencias, matriz, Playwright y enlaces de entrega."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'docs/evidencias-s14'
OUT = ROOT / 'output/pdf/Suarez_LP2_S14_Practica.pdf'
pdfmetrics.registerFont(TTFont('S14', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('S14B', 'C:/Windows/Fonts/arialbd.ttf'))
AZUL = HexColor('#16345c')
styles = {
 'titulo': ParagraphStyle('titulo', fontName='S14B', fontSize=18, leading=23, textColor=AZUL, spaceAfter=7),
 'texto': ParagraphStyle('texto', fontName='S14', fontSize=10, leading=13.5, spaceAfter=7),
 'seccion': ParagraphStyle('seccion', fontName='S14B', fontSize=11.5, leading=15, spaceBefore=9, spaceAfter=6, textColor=AZUL),
 'celda': ParagraphStyle('celda', fontName='S14', fontSize=9, leading=11.5),
 'pequeno': ParagraphStyle('pequeno', fontName='S14', fontSize=8.5, leading=11, spaceAfter=6, textColor=HexColor('#414b5a')),
}
story = []
def p(t, estilo='texto'): story.append(Paragraph(t, styles[estilo]))
def h(t): p(t, 'seccion')
def tabla(rows, widths):
 data = [[Paragraph(escape(str(c)), styles['celda']) for c in row] for row in rows]
 t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
 t.setStyle(TableStyle([
  ('BACKGROUND',(0,0),(-1,0),HexColor('#eaf0f7')),
  ('VALIGN',(0,0),(-1,-1),'TOP'),
  ('LINEBELOW',(0,0),(-1,-1),0.35,HexColor('#d6dfeb')),
  ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
  ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
 ]))
 story.extend([t, Spacer(1,7)])

resultado = json.loads((E/'09-playwright-resumen.json').read_text(encoding='utf-8'))
assert resultado['stats']['expected'] == 21 and resultado['stats']['unexpected'] == 0
assert all(c['aprobadas'] == 7 for c in resultado['corridas'])
mediciones = json.loads((E/'02-mediciones-despues.json').read_text(encoding='utf-8'))['records']
integracion = json.loads((E/'08-integracion.json').read_text(encoding='utf-8'))
assert integracion['aprobadas'] == 8
venta = integracion['corridas'][-1]

p('LP II - Práctica S14', 'titulo')
p('Jatniel Jair Suarez Vigo · 13/11/2026')
p('Se implementó la paginación en Productos y Ventas, la auditoría con V4 y la integración entre módulos. Las ramas y los PR están publicados.')
h('Tabla de evidencias')
p('Carga de prueba: <b>5000 productos y 20000 ventas</b>. Total después de cargar: <b>5015 productos y 20029 ventas</b>. Repetir el script no duplicó registros.')
labels = ['Productos: página 0, tamaño 20', 'Productos: página 0, tamaño 100', 'Productos: página 249, tamaño 20', 'Productos: tamaño 500', 'Orden inválido', 'Ventas: 01 al 12/11, página 0', 'Productos: última página (250)']
indices = [0,1,2,6,3,5]
rows = [['Consulta','HTTP','Tiempo (ms)','Bytes']]
for i in indices:
 r = mediciones[i]
 rows.append([labels[i], r['status'], f"{r['milliseconds']:.3f}", r['bodyBytes']])
tabla(rows, [255,45,100,100])
p('Mediciones individuales del cuerpo JSON. La última página contiene 15 productos. Hibernate generó OFFSET/FETCH y COUNT. Los totales aumentaron después por los datos creados en las pruebas E2E.', 'pequeno')
h('Auditoría y permisos')
p('V4 aplicada: <b>7 columnas y 3 índices</b>. Solo admin consulta la bitácora; vendedor y almacenero reciben <b>403</b>. El login fallido queda registrado y una venta revertida no deja un evento confirmado.')
p(f"Venta <b>{venta['ventaId']}</b> · usuario <b>vendedor</b> · requestId <b>{venta['requestId']}</b> · stock <b>{venta['stockAntes']} a {venta['stockDespues']}</b>.")

class Captura(Flowable):
 def __init__(self):
  super().__init__(); self.width=500; self.height=200
 def draw(self):
  reader=ImageReader(str(E/'07-auditoria-spa.png')); w,h=reader.getSize(); alto=h*self.width/w
  self.canv.saveState(); clip=self.canv.beginPath(); clip.rect(0,0,self.width,self.height)
  self.canv.clipPath(clip,stroke=0,fill=0)
  self.canv.drawImage(reader,0,self.height-alto,width=self.width,height=alto)
  self.canv.restoreState()
story.append(Captura())

story.append(PageBreak())
h('Paso 8. Integrar los módulos')
tabla([
 ['ID','Comprobación','Resultado'],
 ['I-01','Cliente recién registrado disponible en Nueva venta.','Cumple'],
 ['I-02','Solo productos activos con stock, al precio vigente.','Cumple'],
 ['I-03','Vender 2 unidades descuenta stock sin F5.','Cumple'],
 ['I-04','La venta suma en el reporte: 2 unidades y S/ 25.00.','Cumple'],
 ['I-05','Evento de venta con usuario y requestId correctos.','Cumple'],
 ['I-06','Cambio de precio registrado y modificadoPor=admin.','Cumple'],
 ['I-07','Sesión vencida: login y retorno a la ruta de venta.','Cumple'],
 ['I-08','Cambiar fechas desde página 5 vuelve a página 1.','Cumple'],
], [48,382,70])
p('Matriz: <b>8/8</b>. I-07 usa el reloj controlado de la SPA para simular el vencimiento.', 'pequeno')
h('Paso 9. Pruebas end-to-end con Playwright')
tabla([
 ['Prueba','Corrida 1','Corrida 2','Corrida 3'],
 ['Ruta protegida al login','OK','OK','OK'],
 ['Credenciales incorrectas','OK','OK','OK'],
 ['Retorno al destino y vencimiento de sesión','OK','OK','OK'],
 ['Flujo de venta, stock, reportes y auditoría','OK','OK','OK'],
 ['Paginación, F5 y filtros','OK','OK','OK'],
 ['Almacenero sin acceso a Ventas','OK','OK','OK'],
 ['Vendedor sin edición ni acceso a auditoría','OK','OK','OK'],
 ['Total','7/7','7/7','7/7'],
], [290,70,70,70])
p('<b>21/21 aprobadas</b>, un trabajador y cero reintentos. Maven: <b>23 pruebas aprobadas</b>. Sin errores de consola ni respuestas 500 durante el flujo verificado.')
h('Paso 10. Registrar, corregir y volver a probar')
p('<b>6 incidencias registradas y 6 cerradas:</b> límite de página, filtros en URL, selector de filas, búsqueda de productos, Flyway y aserciones del test. No quedan incidencias funcionales altas ni críticas abiertas.')
h('Paso 11. Versionar el trabajo')
p('Rama publicada en ambos repositorios: <b>feature/integracion-estabilizacion-suarez</b>. Cada una contiene más de tres commits y su PR hacia develop.')
p('Backend: <link href="https://github.com/JanislyIsa/pharmaSoft/pull/4" color="#16345c">github.com/JanislyIsa/pharmaSoft/pull/4</link><br/>Frontend: <link href="https://github.com/JanislyIsa/pharma-frontend/pull/5" color="#16345c">github.com/JanislyIsa/pharma-frontend/pull/5</link>')
p('Evidencias e informe HTML: docs/evidencias-s14/. Incidencias y matriz completa: docs/incidencias.md y docs/s14-matriz-integracion.md, en el backend.', 'pequeno')

def pie(canvas,doc):
 canvas.setFont('S14',8); canvas.setFillColor(HexColor('#657086')); canvas.drawRightString(547,24,str(doc.page))
OUT.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(OUT),pagesize=(595,842),leftMargin=48,rightMargin=47,topMargin=33,bottomMargin=34,
 title='LP II - Práctica S14',author='Jatniel Jair Suarez Vigo').build(story,onFirstPage=pie,onLaterPages=pie)
print(OUT)
