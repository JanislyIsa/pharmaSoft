"""Informe breve con evidencia verificada; ejecutar después de consolidar y grabar."""
import json
from pathlib import Path
import subprocess
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidencias/s14-estabilizacion'
P=ROOT/'output/pdf/Suarez_LP2_S14_Autonoma.pdf'
NAVY=colors.HexColor('#12315d');GRAY=colors.HexColor('#526579')
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')
styles={
 'title':ParagraphStyle('title',fontName='Arial-Bold',fontSize=21,leading=26,textColor=NAVY,spaceAfter=8),
 'h':ParagraphStyle('h',fontName='Arial-Bold',fontSize=13,leading=17,textColor=NAVY,spaceBefore=12,spaceAfter=7),
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10,leading=14,spaceAfter=7,textColor=colors.HexColor('#233d57')),
 'small':ParagraphStyle('small',fontName='Arial',fontSize=8.7,leading=12,spaceAfter=5,textColor=GRAY),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=12,textColor=NAVY),
 'head':ParagraphStyle('head',fontName='Arial-Bold',fontSize=9,leading=12,textColor=colors.white),
}
story=[]
def p(t,kind='body'):return Paragraph(t,styles[kind])
def add(t,kind='body'):story.append(p(t,kind))
def link(label,url):return f'<link href="{escape(url)}" color="#145b9b"><u>{escape(label)}</u></link>'
def tabla(rows,widths):
    data=[[p(escape(str(c)),'head' if i==0 else 'cell') for c in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f2f5fa'),colors.white]),('LINEBELOW',(0,0),(-1,0),.5,NAVY),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#dbe3ee'))]))
    story.append(t);story.append(Spacer(1,7))
def imagen(file,width=510,maxh=240):
    obj=Image(str(file));s=min(width/obj.imageWidth,maxh/obj.imageHeight)
    obj.drawWidth=obj.imageWidth*s;obj.drawHeight=obj.imageHeight*s;obj.hAlign='LEFT';story.append(obj);story.append(Spacer(1,6))
def main():
    r=json.loads((E/'playwright-resumen.json').read_text(encoding='utf-8'))
    post=json.loads((E/'postman-resumen.json').read_text(encoding='utf-8'))
    tr=json.loads((E/'trazabilidad.json').read_text(encoding='utf-8'))['resultado']
    manual=json.loads((E/'recorridos-manuales.json').read_text(encoding='utf-8'))['recorridos']
    vid=json.loads((E/'video.json').read_text(encoding='utf-8'))
    assert r['stats']['expected']==42 and post['assertions']==26
    base='https://github.com/JanislyIsa/pharmaSoft/blob/v1.0-demo/docs/'
    add('Actividad autónoma S14','title')
    add('Jatniel Jair Suarez Vigo · Lenguaje de Programación II · 15/11/2026','small')
    add('Parte A. Auditoría: completar y documentar','h')
    add('Se completó /auditoria con permiso USUARIOS_ADMINISTRAR, filtros en la URL y paginador reutilizable. Se separó el ID y se añadieron <b>CLIENTE_REGISTRADO</b> y <b>VENTA_ANULADA</b>. Los cambios de negocio se registran después del commit; el login fallido usa su propia transacción.')
    add('La bitácora no guarda contraseñas, tokens ni cuerpos completos. El alta de cliente guarda estado, sin copiar DNI o correo. '+link('Explicación y tabla de siete eventos',base+'auditoria.md')+'.','small')
    add(f'<b>Venta trazada: {tr["ventaId"]}</b>. creado_por = {tr["creadoPor"]}; evento {tr["accion"]}; requestId = <b>{tr["requestId"]}</b>. La fila y el log coinciden con el comprobante del primer recorrido por interfaz.')
    imagen(E/'trazabilidad-bd.png',maxh=246)
    imagen(E/'trazabilidad-log.png',maxh=172)
    add('Salidas reales de Oracle y de la consola, renderizadas para facilitar lectura. No son capturas de SQL Developer. '+link('Consulta y líneas originales',base+'evidencias/s14-estabilizacion/trazabilidad.json')+'.','small')
    add('La anulación conserva la regla existente: cambia estado; no representa una devolución automática de inventario. La auditoría posterior al commit no tiene outbox durable.','small')
    story.append(PageBreak())
    add('Pruebas e incidencias','title')
    add('Parte B. Pruebas end-to-end','h')
    add('La suite pasó de 7 a <b>14 casos</b>. Se ejecutó con --repeat-each=3: <b>42/42 aprobadas</b>, cero fallidas, flaky u omitidas, sin reintentos ni esperas fijas en e2e/. Duración: <b>75,61 s</b>. Backend '+r['versiones']['backend'][:7]+'; frontend '+r['versiones']['frontend'][:7]+'.')
    imagen(E/'playwright-resultados.png',maxh=119)
    add('Los casos nuevos cubren stock concurrente con 409 sin venta, venta vacía, cliente nuevo e inmediato, fechas desde página 3, auditoría admin/anulación, vendedor sin auditoría y token alterado con 401. '+link('HTML y resultados por caso',base+'resultados-pruebas.md')+'.','small')
    tabla([['Postman real: 18 solicitudes / 26 asserts, todos aprobados','Código'],['Consulta / creación y venta confirmada','200 / 201'],['Venta vacía / sin token / sin permiso','400 / 401 / 403'],['Producto inexistente / stock insuficiente','404 / 409']],[420,90])
    add('Maven: <b>23 pruebas aprobadas</b> y BUILD SUCCESS. Angular: build de producción correcto; persiste un aviso de CSS de venta por 57 bytes sobre el presupuesto de aviso. '+link('Colección importable',base+'postman/PharmaBackend.postman_collection.json')+'.','small')
    add('Parte C. Registro de incidencias','h')
    tabla([['Incidencia','Nivel','Estado'],['01 Tamaño >100; 04 búsqueda incompleta; 05 Flyway','Alta (3)','Cerradas'],['02 URL; 03 selector; 07 Chromium; 08 etiqueta Acción','Media (4)','Cerradas'],['06 formato decimal y producto fuera de página 1','Baja (1)','Cerrada']],[350,80,80])
    add('Se documentaron ocho incidencias con reproducción, esperado/obtenido, causa, corrección, commit y regresión. No queda ninguna crítica o alta abierta. Chromium faltante produjo 42 errores de arranque; después Acción produjo 39/42. Se revisó la traza, se corrigió aria-label y se verificó una suite nueva de 42/42. '+link('Registro completo',base+'incidencias.md')+'.','small')
    story.append(PageBreak())
    add('Demostración y entrega','title')
    add('Parte D. Guion y verificación del flujo','h')
    tabla([['Tiempo','Bloque'],['0:00–1:00','Problema, usuarios y arquitectura'],['1:00–4:30','Vendedor: cliente, productos, venta, comprobante y stock'],['4:30–6:00','Permisos, URL denegada, sesión expirada y 401/403'],['6:00–7:30','5 000 productos, URL, Redis y Actuator'],['7:30–8:30','Venta, bitácora y requestId del log'],['8:30–10:00','Suite en vivo e incidencias cerradas']],[90,420])
    tabla([['Interfaz, 15/11/2026','Venta','Duración','Stock'],*[[f'Recorrido {i+1}',str(x['ventaId']),f'{x["segundos"]} s','20 a 19'] for i,x in enumerate(manual)]],[190,90,110,120])
    add('Recorridos operados por el asistente con tres productos recién preparados, sin vaciar la base. Los tiempos incluyen las pausas anotadas. '+link('Capturas y desvíos',base+'verificacion-flujo.md')+'.','small')
    add(f'Video técnico automatizado: <b>{vid["segundos"]//60}:{vid["segundos"]%60:02d}</b>, seis bloques y ejecución real de la suite. '+link('Abrir video de respaldo',base+'evidencias/s14-estabilizacion/demo-respaldo.mp4')+'. No sustituye una sustentación personal.','small')
    add('Parte E. Evidencias y defensa técnica','h')
    add('Se organizó docs/ con índice, arquitectura, auditoría, incidencias, resultados, guion, checklist, diez respuestas con referencias al código y carpetas por unidad/S13/S14. '+link('Índice de evidencias',base+'README.md')+' · '+link('Arquitectura',base+'arquitectura.png')+' · '+link('Defensa técnica',base+'defensa-tecnica.md')+'.','small')
    add('Parte F. Versionamiento y entrega','h')
    add('Ambos repositorios tienen commits reales en al menos tres días distintos y versión v1.0-demo. '+link('Backend','https://github.com/JanislyIsa/pharmaSoft/tree/v1.0-demo')+' · '+link('Frontend','https://github.com/JanislyIsa/pharma-frontend/tree/v1.0-demo')+'. Las ramas de integración y los PR se conservan para revisión.','small')
    add('Unidad I: se recuperaron trece capturas originales del informe técnico de agosto y de S04/S05. Se conservaron sin editar, con procedencia; la validación actual está separada.','small')
    add('<b>Pendiente del estudiante:</b> hacer dos ensayos orales cronometrados con el guion, revisar las respuestas con sus propias palabras y subir este PDF al aula virtual.','small')
    P.parent.mkdir(parents=True,exist_ok=True)
    def footer(c,doc):
        c.setFont('Arial',8);c.setFillColor(GRAY);c.drawRightString(A4[0]-42,23,str(doc.page))
    doc=SimpleDocTemplate(str(P),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=35,title='Actividad autónoma S14',author='Jatniel Jair Suarez Vigo')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('Informe generado:',P)

if __name__=='__main__':main()
