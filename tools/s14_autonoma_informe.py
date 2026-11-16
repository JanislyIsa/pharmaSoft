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
    add('La página Auditoría tiene filtros, paginación y acceso solo para usuarios autorizados. Se añadieron <b>CLIENTE_REGISTRADO</b> y <b>VENTA_ANULADA</b>. Se registran al confirmar la operación, sin guardar contraseñas ni tokens.')
    add(f'Venta <b>{tr["ventaId"]}</b>, registrada por <b>{tr["creadoPor"]}</b>. Su evento y el log comparten el requestId <b>{tr["requestId"]}</b>.')
    imagen(E/'trazabilidad-bd.png',maxh=145)
    imagen(E/'trazabilidad-log.png',maxh=120)
    add('Salidas reales de Oracle y del log, preparadas para facilitar la lectura. '+link('Detalle de auditoría',base+'auditoria.md')+'.','small')
    add('Parte B. Pruebas end-to-end','h')
    add('<b>14 pruebas, repetidas tres veces: 42/42 aprobadas</b>, sin fallos ni reintentos. Duración: <b>75,61 segundos</b>. Se comprobaron ventas, stock, filtros, permisos y sesión.')
    imagen(E/'playwright-resultados.png',maxh=94)
    tabla([['Postman: 18 solicitudes y 26 comprobaciones aprobadas','Código'],['Consultas y creación de registros','200 / 201'],['Datos inválidos, sin sesión o sin permiso','400 / 401 / 403'],['Producto inexistente o stock insuficiente','404 / 409']],[420,90])
    add('Backend: <b>23 pruebas aprobadas</b>. Frontend: compilación correcta. '+link('Resultados e informe HTML',base+'resultados-pruebas.md')+' · '+link('Colección Postman',base+'postman/PharmaBackend.postman_collection.json')+'.','small')
    story.append(PageBreak())
    add('Demostración y entrega','title')
    add('Parte C. Registro de incidencias','h')
    tabla([['Incidencia','Nivel','Estado'],['01 Tamaño >100; 04 búsqueda incompleta; 05 Flyway','Alta (3)','Cerradas'],['02 URL; 03 selector; 07 Chromium; 08 etiqueta Acción','Media (4)','Cerradas'],['06 formato decimal y producto fuera de página 1','Baja (1)','Cerrada']],[350,80,80])
    add('<b>Ocho incidencias cerradas</b>. Cada una incluye fecha, pasos, causa, corrección, commit y prueba. No quedan incidencias críticas ni altas abiertas. '+link('Registro completo',base+'incidencias.md')+'.','small')
    add('Parte D. Guion y verificación del flujo','h')
    tabla([['Tiempo','Bloque'],['0:00–1:00','Problema, usuarios y arquitectura'],['1:00–4:30','Vendedor: cliente, productos, venta, comprobante y stock'],['4:30–6:00','Permisos, URL denegada, sesión expirada y 401/403'],['6:00–7:30','5 000 productos, URL, Redis y Actuator'],['7:30–8:30','Venta, bitácora y requestId del log'],['8:30–10:00','Suite en vivo e incidencias cerradas']],[90,420])
    tabla([['Interfaz, 15/11/2026','Venta','Duración','Stock'],*[[f'Recorrido {i+1}',str(x['ventaId']),f'{x["segundos"]} s','20 a 19'] for i,x in enumerate(manual)]],[190,90,110,120])
    add('Tres recorridos realizados por el asistente con datos de prueba. '+link('Capturas y observaciones',base+'verificacion-flujo.md')+'.','small')
    add(f'Video de respaldo automatizado: <b>{vid["segundos"]//60}:{vid["segundos"]%60:02d}</b>. '+link('Ver video',base+'evidencias/s14-estabilizacion/demo-respaldo.mp4')+' · '+link('Guion e instrucciones para ensayar',base+'guion-demostracion.md')+'.','small')
    add('Parte E. Evidencias y defensa técnica','h')
    add('Se organizaron las evidencias por unidad, S13 y S14, incluyendo trece capturas originales de Unidad I. Se prepararon la arquitectura, el checklist y diez respuestas con referencias al código. '+link('Índice completo',base+'README.md')+' · '+link('Defensa técnica',base+'defensa-tecnica.md')+'.','small')
    add('Parte F. Versionamiento y entrega','h')
    add('Los dos repositorios tienen commits en tres días distintos y la etiqueta <b>v1.0-demo</b>. '+link('Backend','https://github.com/JanislyIsa/pharmaSoft/tree/v1.0-demo')+' · '+link('Frontend','https://github.com/JanislyIsa/pharma-frontend/tree/v1.0-demo')+'.','small')
    add('<b>Falta:</b> realizar los dos ensayos orales, repasar la defensa y entregar este informe en el aula virtual.','small')
    P.parent.mkdir(parents=True,exist_ok=True)
    def footer(c,doc):
        c.setFont('Arial',8);c.setFillColor(GRAY);c.drawRightString(A4[0]-42,23,str(doc.page))
    doc=SimpleDocTemplate(str(P),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=35,title='Actividad autónoma S14',author='Jatniel Jair Suarez Vigo')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('Informe generado:',P)

if __name__=='__main__':main()
