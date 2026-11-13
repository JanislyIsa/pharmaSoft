"""Informe sencillo S14 a partir de evidencias verificadas, sin encabezados repetidos."""
from pathlib import Path
import json,re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidencias-s14'
OUT=ROOT/'output/pdf/Suarez_LP2_S14_Practica.pdf'
font=Path('C:/Windows/Fonts/arial.ttf');bold=Path('C:/Windows/Fonts/arialbd.ttf')
pdfmetrics.registerFont(TTFont('ArialS14',str(font)));pdfmetrics.registerFont(TTFont('ArialS14B',str(bold)))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TextoS14',fontName='ArialS14',fontSize=9.5,leading=13,spaceAfter=7,textColor=HexColor('#233044')))
styles.add(ParagraphStyle(name='TituloS14',fontName='ArialS14B',fontSize=19,leading=24,spaceAfter=12,textColor=HexColor('#12315d')))
styles.add(ParagraphStyle(name='PasoS14',fontName='ArialS14B',fontSize=11.5,leading=15,spaceBefore=9,spaceAfter=6,textColor=HexColor('#12315d')))
styles.add(ParagraphStyle(name='CeldaS14',fontName='ArialS14',fontSize=8,leading=10))
story=[]
def p(t):story.append(Paragraph(t,styles['TextoS14']))
def h(t):story.append(Paragraph(t,styles['PasoS14']))
def tabla(rows,widths):
 data=[[Paragraph(str(c),styles['CeldaS14']) for c in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e9eef6')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),0.4,HexColor('#d8e0eb')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(t);story.append(Spacer(1,9))
def page():story.append(PageBreak())
summary=json.loads((E/'09-playwright-resumen.json').read_text(encoding='utf-8'))
assert len(summary['pruebas'])==21 and all(x['estado']=='expected' for x in summary['pruebas'])
vol=json.loads((E/'08-volumen-final.json').read_text(encoding='utf-8'))['sql']
prod=re.search(r'PRODUCTOS=(\d+)',vol).group(1);ventas=re.search(r'VENTAS=(\d+)',vol).group(1)
info=json.loads((E/'08-integracion.json').read_text(encoding='utf-8'))
example=info['corridas'][-1]
story.append(Paragraph('LP II - Práctica S14',styles['TituloS14']))
p('Jatniel Jair Suarez Vigo<br/>13 de noviembre de 2026')
h('Paso 1. Crear las ramas de trabajo')
p('Se creó <b>feature/integracion-estabilizacion-suarez</b> en backend y frontend, desde develop e integrando el avance S13. Se conservaron los archivos de actividades anteriores.')
h('Paso 2. Cargar volumen de prueba y medir la línea base')
p('El script docs/sql/volumen_pruebas.sql agregó 5000 productos y 20000 ventas sin detalle en Oracle local. Tras la carga había 5015 productos y 20029 ventas. Repetirla insertó 0 filas. Las ventas sintéticas son para medir listados, no para validar reportes.')
tabla([['Consulta','HTTP','Tiempo (ms)','Cuerpo (bytes)'],['Productos página 0, tamaño 20','200','250.013','4722'],['Productos página 0, tamaño 100','200','79.022','23441'],['Productos página 249, tamaño 20','200','63.719','4783'],['Productos última real: 250','200','57.101','3588'],['Productos tamaño 500','409','34.146','233'],['Ventas 01 al 12/11, página 0','200','276.455','3126']],[235,45,95,125])
p('Son peticiones individuales, no promedios. Hibernate generó OFFSET/FETCH y COUNT. La página 249 del ejemplo no era la última porque ya existían 15 productos. Antes de corregir el límite, tamaño 500 devolvía HTTP 200 y 117003 bytes.')
h('Paso 3. Paginar en la SPA: modelo, servicio y paginador')
p('Se agregaron Pagina/ConsultaPagina y un paginador compartido con primera, anterior, siguiente, última, tamaño y total. Productos y Ventas lo reutilizan. El backend acepta de 1 a 100 filas y usa 20 por defecto.')
h('Paso 4. La lista de productos con la página en la URL')
p('Página, tamaño, orden y filtros se guardan en la URL. F5 e historial conservan la consulta. Cambiar filtros vuelve a página 0. rxResource cancela solicitudes anteriores y linkedSignal mantiene la tabla mientras carga. Se comprobó también en Ventas, desde la página 5.')
page()
h('Paso 5. Auditoría en el backend: migración V4')
p('V4__auditoria.sql incorpora siete columnas de autoría, auditoria_eventos e índices por fecha, usuario y nombre de producto. Flyway registró V4 con success=1. El esquema queda con ddl-auto=validate.')
p('Se corrigió la falta del starter de Flyway en Spring Boot 4. Como la base ya tenía las tablas de seguridad V2, se registró baseline 2. V4 conserva objetos presentes en desarrollo. Un intento de V4 falló por una declaración PL/SQL; se corrigió antes de aplicarla y se utilizó Flyway Repair únicamente sobre ese intento fallido.')
h('Paso 6. Columnas de auditoría con Spring Data JPA')
p('AuditorAware toma el usuario autenticado del token; un proceso sin usuario utiliza sistema. Producto, Categoría y Cliente guardan creadoPor y modificadoPor; Venta guarda creadoPor. Los DTO incluyen esos campos. La edición del producto y el detalle de venta los muestran.')
h('Paso 7. Bitácora de eventos')
p('Registra LOGIN_EXITOSO, LOGIN_FALLIDO, VENTA_REGISTRADA, PRECIO_MODIFICADO y PRODUCTO_ELIMINADO. Los eventos de negocio se guardan después del commit, en una transacción nueva. El login fallido se registra directamente. No se guardan contraseñas ni tokens.')
p('GET /api/v1/auditoria permite filtrar usuario, acción y fechas, con paginación. Solo USUARIOS_ADMINISTRAR puede consultarlo. Vendedor y almacenero recibieron 403; admin recibió 200. Se agregó una pantalla protegida de Auditoría.')
p(f'Ejemplo verificado: venta {example["ventaId"]}, usuario vendedor, solicitud <b>{example["requestId"]}</b>, stock {example["stockAntes"]} a {example["stockDespues"]}. Una segunda venta que falló no descontó stock ni añadió un evento falso.')
img=E/'07-auditoria-spa.png'
if img.exists():
 from reportlab.lib.utils import ImageReader
 class Captura(Flowable):
  def __init__(self):
   super().__init__();self.width=500;self.height=281.25
  def draw(self):
   reader=ImageReader(str(img));w,h=reader.getSize();alto=h*self.width/w
   self.canv.saveState();clip=self.canv.beginPath();clip.rect(0,0,self.width,self.height);self.canv.clipPath(clip,stroke=0,fill=0)
   self.canv.drawImage(reader,0,self.height-alto,width=self.width,height=alto);self.canv.restoreState()
 story.append(Captura())
page()
h('Paso 8. Integrar los módulos')
tabla([['ID','Integración comprobada','Resultado'],['I-01','Cliente de prueba recién registrado aparece en Nueva venta.','Cumple'],['I-02','El buscador ofrece el producto activo con stock y excluye sus variantes inactiva y agotada.','Cumple'],['I-03','Vender 2 unidades reduce el stock de 20 a 18; Productos lo muestra sin F5.','Cumple'],['I-04','El reporte incluye el nuevo producto: 2 unidades y S/ 25.00.','Cumple'],['I-05','La venta tiene evento, usuario vendedor y requestId idéntico al de la petición.','Cumple'],['I-06','Cambiar precio de 12.50 a 13 registra ambos importes y modificadoPor=admin.','Cumple'],['I-07','Vencimiento controlado del reloj de la SPA: login y retorno a /ventas/nueva.','Cumple'],['I-08','Desde página 5, cambiar fechas vuelve a página 1; F5 conserva filtros.','Cumple']],[45,390,65])
p('Matriz: <b>8/8</b>. I-07 adelanta el reloj de la SPA hasta el vencimiento informado por el backend; no espera una hora real ni modifica la seguridad. Los datos de prueba se crean por corrida; no se borran datos anteriores.')
h('Paso 9. Pruebas end-to-end con Playwright')
p('Se implementaron las siete pruebas en e2e/, con un trabajador, cero reintentos y esperas por estado o respuesta, sin waitForTimeout. El flujo incluye una venta real de dos unidades, rollback, caché, reportes y auditoría.')
tabla([['Grupo','Pruebas'],['Autenticación','Ruta protegida; credenciales incorrectas; retorno al destino y vencimiento.'],['Permisos','Almacenero sin Ventas; vendedor sin edición ni acceso a auditoría.'],['Paginación','Productos y Ventas, F5 y reinicio al cambiar filtros.'],['Flujo principal','Cliente, catálogo, venta, stock, reporte, autoría y bitácora.']],[125,375])
tabla([['Corrida 1','Corrida 2','Corrida 3','Reintentos'],['7/7','7/7','7/7','0']],[125,125,125,125])
p('Resultado final: <b>21/21 aprobadas</b>. Informe HTML: docs/evidencias-s14/playwright-report/index.html. El resumen JSON guarda duración y resultado de cada ejecución.')
page()
h('Paso 10. Registrar, corregir y volver a probar')
tabla([['ID','Causa y corrección','Estado'],['INC-01','Se aceptaba tamaño 500. Se validó el rango 1 a 100.','Cerrada'],['INC-02','Estado local de listados. Se llevó a la URL y se reinicia al filtrar.','Cerrada'],['INC-03','Selector mostraba tamaño incorrecto. Se selecciona la opción real.','Cerrada'],['INC-04','Nueva venta buscaba solo en 100 productos. Se consulta el servidor con debounce y cancelación.','Cerrada'],['INC-05','Flyway no se activaba. Se añadió el starter, baseline y validación del esquema.','Cerrada'],['INC-06','Assert exigía 12.50 y recibía 12.5. Se aceptan representaciones equivalentes sin omitir los importes.','Cerrada']],[60,375,65])
p('La primera corrida fue 6/7 por el formato decimal. Una verificación posterior dio 18/21 porque el producto de prueba quedaba fuera de la primera página. Se corrigió el assert y el test pasó a recorrer el paginador real para localizar el producto, sin F5. Después se volvió a ejecutar la suite triple completa. Las incidencias, sus causas y commits están en docs/incidencias.md. No quedan incidencias funcionales críticas ni altas abiertas.')
p('Maven: <b>23 pruebas aprobadas</b>. Angular: compilación de producción correcta. npm: <b>0 vulnerabilidades</b> tras los parches compatibles de Angular 22. El aviso CSS existente de venta-form.css es de 57 bytes sobre su presupuesto; no impide compilar.')
h('Paso 11. Versionar el trabajo')
p('Las ramas locales contienen al menos tres commits cada una. Se separaron código, pruebas y evidencias. Las modificaciones anteriores de S9, S10 y S13 se dejaron fuera de los commits de esta entrega.')
p('<b>Pendiente externo:</b> publicar las ramas y crear los PR hacia develop. Las descripciones y comandos están preparados en docs/s14-publicacion.md. Este informe no afirma que los PR estén creados.')
p('Backend: <link href="https://github.com/JanislyIsa/pharmaSoft" color="#12315d">github.com/JanislyIsa/pharmaSoft</link><br/>Frontend: <link href="https://github.com/JanislyIsa/pharma-frontend" color="#12315d">github.com/JanislyIsa/pharma-frontend</link>')
h('Tabla de evidencias')
tabla([['Evidencia','Valor'],['Carga inicial','5015 productos / 20029 ventas'],['Volumen final, incluidas las corridas',f'{prod} productos / {ventas} ventas'],['Integración / E2E','8/8 filas / 7/7 en cada una de las tres corridas'],['V4 e índices','V4 aplicada; 7 columnas; 3 índices'],['Incidencias registradas / cerradas','6 / 6'],['Consola y respuestas 500 del flujo','Sin errores de navegador ni respuestas 500 en las corridas aprobadas']],[250,250])
OUT.parent.mkdir(parents=True,exist_ok=True)
def pie(canvas,doc):
 canvas.setFont('ArialS14',8);canvas.setFillColor(HexColor('#657086'));canvas.drawRightString(545,25,str(doc.page))
SimpleDocTemplate(str(OUT),pagesize=(595,842),rightMargin=47,leftMargin=48,topMargin=35,bottomMargin=40,title='LP II - Práctica S14',author='Jatniel Jair Suarez Vigo').build(story,onFirstPage=pie,onLaterPages=pie)
print(OUT)
