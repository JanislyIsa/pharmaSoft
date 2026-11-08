"""Genera el informe autónomo a partir de los registros de pruebas locales."""
from html import escape
import json
import os
from pathlib import Path
import shutil

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT.parent / 'pharma-frontend'
EVID = FRONT / 'docs/evidencias-s13-autonoma'
OUT = ROOT / 'docs/informe-s13.pdf'
CLASSROOM = FRONT / 'output/pdf/Suarez_LP2_S13_Autonoma.pdf'
INK, BLUE, MUTED, LINE, TINT, GOLD = map(colors.HexColor, [
    '#142239', '#112F5B', '#465875', '#DBE4EE', '#F2F6FB', '#ECAA13'])
W = A4[0] - 96
story = []
fonts = Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts'
for name, file in [('S13', 'segoeui.ttf'), ('S13Bold', 'segoeuib.ttf'), ('S13Mono', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
pdfmetrics.registerFontFamily('S13', normal='S13', bold='S13Bold', italic='S13', boldItalic='S13Bold')

def data(path):
    return json.loads((EVID / path).read_text(encoding='utf-8'))

def fmt(v, places=0):
    return f'{v:,.{places}f}'.translate(str.maketrans(',.', '.,'))

def add(s, size=10.5, color=INK, bold=False, leading=None, after=7):
    s = s.replace('face="Courier"', 'face="S13Mono"')
    style = ParagraphStyle('text', fontName='S13Bold' if bold else 'S13',
                           fontSize=size, leading=leading or size*1.35, textColor=color, spaceAfter=after)
    story.append(Paragraph(s, style))

def section(code, title, note):
    add(code, 10, BLUE, True, after=6)
    add(title, 25, BLUE, True, after=7)
    add(note, 10.5, MUTED, after=16)

def sub(title):
    add(title, 13, BLUE, True, after=6)

def table(headers, rows, widths, font=9):
    cell = ParagraphStyle('cell', fontName='S13', fontSize=font, leading=font*1.29, textColor=INK)
    head = ParagraphStyle('head', parent=cell, fontName='S13Bold', textColor=colors.white)
    values = [[Paragraph(escape(str(x)), head) for x in headers]]
    values.extend([[Paragraph(escape(str(x)), cell) for x in row] for row in rows])
    t = Table(values, colWidths=[W * x for x in widths], hAlign='LEFT', repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BLUE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TINT]),
        ('LINEBELOW', (0,0), (-1,-1), .35, LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 5.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5.5),
    ]))
    story.extend([t, Spacer(1, 10)])

def image(path, caption, maxh=260, crop=None):
    from io import BytesIO
    source = PILImage.open(EVID / path).convert('RGB')
    if crop:
        x0, y0, x1, y1 = crop
        source = source.crop(tuple(int(f*d) for f,d in zip((x0,y0,x1,y1), source.size*2)))
    scale = min(W / source.width, maxh / source.height)
    buf = BytesIO()
    source.save(buf, format='PNG')
    buf.seek(0)
    pic = Image(buf, width=source.width*scale, height=source.height*scale)
    pic.hAlign = 'LEFT'
    story.append(pic)
    story.append(Spacer(1, 4))
    add(caption, 8.3, MUTED, after=9)

def block(lines, font=8.5):
    style=ParagraphStyle('mono', fontName='S13Mono', fontSize=font, leading=font*1.3, textColor=BLUE)
    para=Paragraph('<br/>'.join(escape(line) for line in lines), style)
    t=Table([[para]], colWidths=[W], hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TINT),
                           ('BOX',(0,0),(-1,-1),.5,LINE),
                           ('LEFTPADDING',(0,0),(-1,-1),9),
                           ('TOPPADDING',(0,0),(-1,-1),8),
                           ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.extend([t, Spacer(1, 10)])

def product_comparison():
    from io import BytesIO
    items=[]
    captions=[]
    for stage, label in [('antes', 'Antes: texto original'), ('despues', 'Después: texto nuevo')]:
        src=PILImage.open(EVID / f'B/B-{stage}-despliegue.png').convert('RGB')
        w,h=src.size
        crop=src.crop((int(w*.197), int(h*.105), int(w*.57), int(h*.278)))
        buf=BytesIO()
        crop.save(buf, format='PNG')
        buf.seek(0)
        half=W/2-12
        items.append(Image(buf,width=half,height=half*crop.height/crop.width))
        captions.append(Paragraph(label,ParagraphStyle('cap',fontName='S13Bold',fontSize=8.5,textColor=BLUE)))
    pair=Table([captions,items],colWidths=[W/2,W/2],hAlign='LEFT')
    pair.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('BACKGROUND',(0,0),(-1,-1),TINT),
                              ('BOX',(0,0),(-1,-1),.4,LINE)]))
    story.extend([pair,Spacer(1,4)])
    add('B-antes-despliegue.png y B-despues-despliegue.png · Recortes de la misma vista de Productos.',8.3,MUTED)

def page():
    story.append(PageBreak())

build = data('A/A-resumen-builds.json')
ab = data('A/A-comparacion-precarga.json')
before, after = data('B/B-manifiesto-antes.json'), data('B/B-manifiesto-despues.json')
reload = data('B/B-recarga-normal.json')
fresh = data('B/B-despues-despliegue.json')
head = data('B/B-curl-head.json')
cache = data('C/C-aciertos-20x2.json')['series']
ttl = data('C/C-ttl-1-minuto.json')['muestras']
restored = data('C/C-ttl-restaurado.json')
matrix = {x['id']:x for x in data('C/C-matriz.json')}
down = data('C/C-06-redis-down.json')
up = data('D/D-health-up.json')
trace = data('D/D-venta-traza.json')
err = next(x for x in data('D/D-error-spa.json')['requests'] if x['status']==404)
audit = data('D/D-auditoria-y-metricas.json')
ms = {x['statistic']:x['value'] for x in audit['metricsVentas']['measurements']}
assert head['sameContainer'] and '304' in head['indexConditional']
assert before['containerId']==after['containerId'] and before['startedAt']==after['startedAt']
assert err['requestId']==err['bodyRequestId'] and len(trace['logLines'])==4
assert all(x['passed'] for x in matrix.values())

section('LENGUAJE DE PROGRAMACIÓN II  /  SESIÓN 13',
        'Optimización y preparación para producción de PharmaSoft',
        'Actividad autónoma · Reto 02 · Semestre 2026-2')
add('Jatniel Jair Suarez Vigo', 14, BLUE, True, after=3)
add('Facultad de Ingeniería y Arquitectura · Ingeniería de Sistemas<br/>Docente: Benjamin David Reyna Barreto · Mediciones: 8 de noviembre de 2026', 10, MUTED, after=20)
sub('Resultados principales')
table(['Prueba', 'Resultado observado'], [
    ('Entrega inicial', '318.190 → 306.910 bytes de build (−3,54 %).'),
    ('Navegación', 'Sin precarga se transfirieron 52.877 bytes menos antes de abrir Ventas.'),
    ('Caché Redis', '19 de 20 aciertos por caché; seis verificaciones de la matriz correctas.'),
    ('Despliegue', 'Texto nuevo en Productos con una recarga normal y el mismo Nginx.'),
    ('Observabilidad', f'Venta {trace["request"]["entityId"]}: cuatro líneas con el mismo X-Request-Id.'),
], [.32,.68])
sub('Entorno y alcance')
add('Se usó una compilación Angular de producción servida por Nginx en <b>localhost:8081</b>. PharmaBackend corrió en el puerto 8080 con perfil prod, Oracle persistió los datos y Redis funcionó como caché temporal. La prueba de TTL usó un proceso aparte y la base 1 de Redis.')
add('Los resultados corresponden al laboratorio y a los casos ejecutados. Se conservaron capturas y registros JSON junto al código del frontend. La publicación y el requisito de tres días se detallan en la parte F.')
table(['Parte','Contenido'], [('A–B','Paquete inicial, precarga, política de caché y despliegue simulado.'),
                              ('C–D','Aciertos, TTL, invalidación, trazas y monitoreo.'),
                              ('E–F','Despliegue en tres locales y estado de entrega.')],[.20,.80])
page()

section('PARTE A  /  4 PUNTOS', 'Paquete inicial y carga diferida',
        'Dos compilaciones de producción con el mismo comando: ng build --stats-json.')
origins = ['Angular Core · ejecución y renderizado',
           'Angular Router · navegación y guardas',
           'Angular Core · tareas pendientes',
           'Angular Common · cliente HTTP',
           'Angular Common · utilidades comunes']
rows=[]
for i,x in enumerate(build['before']['topInitialModules']):
    name = x['file'].split('/fesm2022/')[-1]
    rows.append((i+1, name, origins[i], fmt(x['bytesInOutput'])))
table(['#','Módulo de entrada','Origen','Bytes aportados'],rows,[.06,.37,.37,.20],8.7)
add('Los cinco módulos son entradas de Angular identificadas en el metafile de esbuild. El nombre de un archivo <font face="Courier">chunk-*.js</font> identifica un resultado de compilación que puede reunir varios módulos. Los bytes aportados son estimaciones del analizador; el total real se toma del build.',9.5)
image('A/A-analyzer.png','A-analyzer.png · Metafile de la compilación anterior en esbuild Bundle Analyzer.',188)
sub('Cambio aplicado y medido')
table(['Indicador','Antes','Después'],[
    ('Initial total bruto','318.190 B','306.910 B'),
    ('Transferencia estimada del build','89,63 kB','86,58 kB'),
    ('Chunks JS diferidos','23','29'),
], [.58,.21,.21])
add('En <b>app.routes.ts</b> pasé el layout y la pantalla de acceso denegado a <font face="Courier">loadComponent</font>. En <b>ventas.routes.ts</b> separé lista, formulario y detalle para descargar cada pantalla al abrirla. El login deja de cargar el layout de una sesión y entrar a Ventas no trae el formulario y el detalle por adelantado.',9.8)
page()

section('PARTE A  /  CONTINUACIÓN', 'Comparación de precarga',
        'Tres ejecuciones por variante con el mismo backend, navegador de 1280 × 720, gzip y caché HTTP deshabilitada por la configuración del banco de pruebas.')
table(['Mediana de 3 corridas','Sin precarga','Con precarga'], [
    ('Bytes hasta clic en Ventas',fmt(ab['sin']['medianaBytesInicio'])+' B',fmt(ab['con']['medianaBytesInicio'])+' B'),
    ('Bytes JS hasta el clic',fmt(ab['sin']['medianaJsBytesInicio'])+' B',fmt(ab['con']['medianaJsBytesInicio'])+' B'),
    ('Clic → título de Ventas',fmt(ab['sin']['medianaVentasHeadingMs'],1)+' ms',fmt(ab['con']['medianaVentasHeadingMs'],1)+' ms'),
    ('Clic → primera fila',fmt(ab['sin']['medianaVentasClickMs'],1)+' ms',fmt(ab['con']['medianaVentasClickMs'],1)+' ms'),
    ('Login aceptado → primera fila',fmt(ab['sin']['medianaVentasLoginMs'],1)+' ms',fmt(ab['con']['medianaVentasLoginMs'],1)+' ms'),
], [.50,.25,.25])
add('Inicio de sesión con el mismo rol y espera de dos segundos en Inicio. Se midió hasta ver una fila, además del título, para incluir la carga de los datos. El intervalo desde el login incluye la espera fijada para ambos escenarios.')
sub('Decisión: conservar la carga diferida sin precarga global')
add('Precargar todo aumentó los bytes previos a Ventas en <b>37,27 %</b> y adelantó la primera fila <b>47,7 ms</b> desde el clic, sin mejorar la aparición del título en la mediana. En los locales con conexión más lenta conviene descargar cada pantalla al usarla. Si Ventas concentra el trabajo, medir una precarga selectiva antes de adoptarla.')
image('A/A-sin-precarga.png','A-sin-precarga.png · Medición en el navegador con la opción predeterminada.',126)
image('A/A-con-precarga.png','A-con-precarga.png · Misma prueba con withPreloading(PreloadAllModules).',126)
page()

section('PARTE B  /  3 PUNTOS', 'Caché HTTP y actualización',
        'Nginx en 8081. Se verificó Cache-Control con curl -I y la transferencia con Resource Timing del navegador durante una recarga normal.')
def transferred(path):
    return next(x['transferSize'] for x in reload['resources'] if x['path']==path)
table(['Recurso','Cache-Control','Origen en la recarga','OK'], [
    ('/index.html','no-cache',f'Revalidación: {reload["navigation"]["transferSize"]} B observados; 304 con If-None-Match en curl.','Sí'),
    (before['main'],'public, max-age=31536000, immutable',f'Caché local: {transferred("/"+before["main"])} B.','Sí'),
    (before['sales'],'public, max-age=31536000, immutable',f'Caché local: {transferred("/"+before["sales"])} B al volver a Ventas.','Sí'),
    (before['styles'],'public, max-age=31536000, immutable',f'Caché local: {transferred("/"+before["styles"])} B.','Sí'),
    ('/api/v1/categorias','no-cache, no-store, max-age=0, must-revalidate',f'Red: {transferred("/api/v1/categorias")} B, HTTP 200.','Sí'),
], [.25,.33,.34,.08],8.6)
add('Resource Timing permite confirmar la reutilización local sin distinguir memoria de disco. El 304 se verificó con una solicitud condicional separada; el navegador expone 200 en la entrada de navegación. No se limpió la caché entre versiones.',9.5)
sub('Simulación de despliegue')
rows=[]
for k, label in [('main','Entrada'),('product','Lista de Productos'),('sales','Lista de Ventas'),('styles','Estilos')]:
    item=next((x for x in fresh['resources'] if x['path']=='/'+after[k]),None)
    received=fmt(item['transferSize'])+' B' if item else 'Fuera de la ruta probada'
    rows.append((label,before[k],after[k],received))
table(['Archivo','Antes','Después','Recarga posterior'],rows,[.22,.25,.25,.28],8.6)
add(f'El contenedor Nginx conservó su ID ({after["containerId"][:12]}) y hora de arranque. El HTML revalidado referencia nombres nuevos para el código que cambió. El CSS conservó su hash y se reutilizó. El nuevo chunk de Ventas aparece en el manifiesto; la recarga de Productos no lo solicita.',9.5)
product_comparison()
add('El API contiene datos autenticados y variables como el stock. Spring Security agrega <b>no-cache, no-store, max-age=0, must-revalidate</b>; así se evita que el navegador reutilice respuestas anteriores o conserve copias de datos de sesión. La caché de Redis actúa en el servidor y se invalida al escribir.',9.2)
page()

section('PARTE C  /  5 PUNTOS', 'Aciertos, tiempos y vigencia',
        'Pruebas con la aplicación recién iniciada y dos claves de prueba retiradas al comenzar cada serie.')
rows=[]
for name, label in [('categorias','GET /categorias'),('productos','GET /productos · página 0')]:
    c = cache[name]
    rows.append((label, '20', f'{int(c["hits"])} / {int(c["misses"])}', f'{c["hitRatePercent"]:.0f} %',
                 fmt(c['firstMissMs'],3)+' ms',fmt(c['meanHitsMs'],3)+' ms'))
table(['Consulta','GET','Hit / miss','Tasa','Primer fallo','Media 19 hit'],rows,[.26,.08,.14,.11,.20,.21],8.6)
add('Para cada caché se restó el contador anterior al posterior en <font face="Courier">/actuator/metrics/cache.gets</font> con las etiquetas <font face="Courier">name</font> y <font face="Courier">result</font>. Tasa: 19 / (19 + 1) = 95 %. Los tiempos se midieron desde el cliente HTTP con un reloj monotónico, incluyendo autorización y transferencia.')
add('El primer GET consulta Oracle y escribe Redis. Los 19 siguientes leen la copia. La diferencia no equivale a un benchmark general: hay un único fallo en frío por serie y la red es local.',9.7)
sub('TTL temporal de un minuto')
table(['Tiempo de muestreo','redis-cli TTL','redis-cli EXISTS'],
      [(fmt(x['seconds'],1)+' s',x['ttl'],x['exists']) for x in ttl],[.36,.32,.32],9)
add(f'La instancia temporal del puerto 8082 escribió en Redis DB 1 con <b>1m</b>. La muestra final devolvió TTL −2 y EXISTS 0, que confirman la expiración. Se detuvo esa instancia. En el backend normal (8080, DB 0), un GET repobló la clave con <b>{restored["ttlSeconds"]} segundos</b>.')
block(['Comandos de verificación en la sesión TTL:',
       'redis-cli -n 1 TTL "categorias::todas"',
       'redis-cli -n 1 EXISTS "categorias::todas"',
       'redis-cli -n 0 TTL "categorias::todas"  →  600'],8.6)
add('Fuentes: C-aciertos-20x2.json · C-ttl-1-minuto.json · C-ttl-restaurado.json.',8.6,MUTED)
page()

section('PARTE C  /  CONTINUACIÓN', 'Matriz de invalidación',
        'Se probaron lecturas después de cada escritura con datos creados para el ensayo. Oracle permaneció activo durante la caída de Redis.')
rows=[
    ('C-01','Crear categoría','Aparece en lista',f'Visible, ID {matrix["C-01"]["categoriaId"]}; clave invalidada.'),
    ('C-02','Renombrar categoría','Lista de productos muestra el nombre nuevo','La categoría del producto 122 muestra el sufijo Edit.'),
    ('C-03','Cambiar precio','Nuevo precio en detalle y lista','S/ 3,25 → S/ 4,50 en ambas vistas.'),
    ('C-04','Registrar venta desde SPA','Stock descontado','8 → 7 tras vender una unidad; venta 161.'),
    ('C-05','Eliminar categoría vacía','Desaparece de la lista','ID 164 ausente; clave invalidada.'),
    ('C-06','Detener Redis','Productos funciona; health DOWN','Productos HTTP 200; health HTTP 503, Redis DOWN.'),
]
table(['ID','Operación','Esperado','Obtenido'],rows,[.11,.24,.27,.38],8.6)
add('C-01 a C-05 verificaron la respuesta inmediatamente posterior a la escritura. No se halló un defecto de invalidación en estos casos. Las escrituras de categorías limpian la caché de categorías y, cuando corresponde, la de productos; editar un producto o registrar una venta limpia productos.')
image('C/C-06-productos-spa.png','C-06-productos-spa.png · La SPA muestra el producto de prueba con precio S/ 4,50 y stock 7, mientras Redis está detenido.',255)
add(f'La comprobación directa de Productos con Redis apagado tomó {fmt(down["productos"]["durationMs"],1)} ms. El manejador de errores de caché permitió consultar Oracle. El retorno a UP se comprobó después de iniciar Redis.',9.4)
page()

section('PARTE D  /  4 PUNTOS', 'Trazabilidad de la venta y los errores',
        'La SPA registró una venta de una unidad del producto de prueba; se relacionó la respuesta HTTP con las líneas del log de producción.')
rec=trace['request']
block([f'POST /api/v1/ventas  →  {rec["status"]} Created',
       f'X-Request-Id: {rec["requestId"]}  |  Venta: {rec["entityId"]}',
       f'Filtro de log: Select-String -SimpleMatch "{rec["requestId"]}"'],9)
notes=['Inicio: una línea de venta para el cliente seleccionado.',
       'Proceso: valida la cantidad del producto de prueba.',
       'Persistencia: confirma la venta y el total de S/ 4,50.',
       'Salida HTTP: el filtro anota estado 201 y duración.']
table(['Hora / mismo identificador','Mensaje de log','Interpretación'],[
    (line.split()[1]+f' [{rec["requestId"]}]',line.split(' - ',1)[1],notes[i])
    for i,line in enumerate(trace['logLines'])
],[.25,.40,.35],8.7)
sub('Identificador visible en la SPA')
add('Agregué <b>requestId</b> a <b>ErrorResponseDTO</b>. <b>GlobalExceptionHandler</b> lee el valor de <font face="Courier">MDC.get("requestId")</font>; las respuestas 401/403 del filtro de seguridad usan el mismo campo. En Angular, <b>http-error.ts</b> lo agrega al mensaje cuando existe. El usuario puede copiarlo y soporte puede filtrar las líneas de esa petición.')
image('D/D-error-spa.png',f'D-error-spa.png · Error 404 real. Cabecera, JSON y alerta muestran {err["requestId"]}.',190)
add('Registros: D-venta-post.json, D-venta-traza.json y D-error-spa.json. Se guardaron los campos de trazabilidad necesarios, sin Authorization ni cuerpo del login.',8.9,MUTED)
page()

section('PARTE D  /  CONTINUACIÓN', 'Salud, métricas y auditoría',
        'Se midió el estado global y los componentes al detener Redis y después de restaurarlo.')
table(['Redis','Health público','Health con token admin','Interpretación'], [
    ('Activo','200 UP; sin detalles','200 UP; Oracle UP y Redis UP','Servicios locales operativos.'),
    ('Detenido','503 DOWN; sin detalles','503 DOWN; Oracle UP y Redis DOWN','Caché caída; el listado sigue sirviéndose desde Oracle.'),
    ('Restaurado','200 UP','200 UP; ambos componentes UP','Terminó la prueba de caída.'),
], [.17,.23,.28,.32],8.8)
image('D/D-health-down.png','D-health-down.png · /actuator/health sin token durante la caída (recorte).',48,(0,0,1,.16))
image('D/D-health-up.png','D-health-up.png · /actuator/health sin token tras restaurar Redis (recorte).',48,(0,0,1,.16))
sub('Métrica http.server.requests · uri:/api/v1/ventas')
table(['COUNT','TOTAL_TIME','MAX','Etiquetas observadas'],[
    (int(ms['COUNT']),fmt(ms['TOTAL_TIME'],6)+' s',fmt(ms['MAX'],6)+' s','POST · 201 · SUCCESS'),
],[.15,.24,.22,.39],9)
add('La métrica representa un POST exitoso en el proceso medido: promedio = total / conteo = 173,444 ms. Con una sola muestra el máximo coincide con el promedio y no describe el rendimiento bajo carga. Vendedor recibió 403 al consultar métricas.')
sub('Auditoría de secretos')
add(f'En {fmt(audit["logBytes"])} bytes del log se buscaron los patrones password, Bearer y secret, la clave JWT, tokens y contraseña de base de datos, y {audit["dniValoresComprobados"]} DNI de clientes conocidos: <b>0 coincidencias en la muestra</b>. Como prevención, el filtro de JWT registra la clase de excepción en vez del mensaje, que podría incluir contenido del token.')
add('Fuentes: D-auditoria-y-metricas.json, D-health-up.json y C-06-redis-down.json. Suite Maven: 15 pruebas, 0 fallos y 0 errores. Build Angular: correcto, con advertencia de 57 B del CSS de Venta.',8.8,MUTED)
page()

section('PARTES E Y F  /  4 PUNTOS', 'Despliegue y entrega',
        'Los dos README incluyen arquitectura, variables sin valores reales, verificación, reversión y una lista de buenas prácticas.')
block(['Navegadores de los 3 locales',
       '  → Nginx (8081 local; HTTPS 443 propuesto)',
       '     → PharmaBackend (8080 privado) para /api/',
       '        → Oracle (1521 interno, 1522 host local)',
       '        → Redis (6379 privado, TTL 10m)'],9)
table(['Prioridad','Acción para los tres locales'],[
    ('1 · Acceso','Publicar una sola URL HTTPS con renovación y mantener backend, Oracle y Redis en red privada.'),
    ('2 · Continuidad','Respaldar Oracle fuera del servidor y probar restauración y reversión en un local antes del despliegue general.'),
    ('3 · Operación','Compartir backend y Redis privado, alertar por health DOWN y 5xx, y medir latencia desde los tres locales.'),
],[.22,.78])
add('Conservar cada JAR y carpeta de frontend por versión. Nginx monta la versión con <b>SPA_DIST</b>; para revertir se monta la anterior. El JAR anterior solo se reinicia si es compatible con el esquema migrado. Verificar health, login y Productos al terminar.')
sub('Versionamiento y entrega')
table(['Requisito','Estado'],[
    ('Ramas de trabajo','feature/optimizacion-produccion-suarez en backend y frontend.'),
    ('Tres días distintos','Trabajo S13 registrado el 5 y el 8 de noviembre. Queda un tercer día real por cumplir en cada repositorio.'),
    ('PDF','Backend: docs/informe-s13.pdf. Copia para el aula: Suarez_LP2_S13_Autonoma.pdf.'),
    ('Solicitudes hacia develop','Pendientes de publicación. Frontend tiene origin/develop; en backend no se encontró esa rama remota en la revisión local.'),
],[.31,.69])
sub('Fuentes y material de sustentación')
add('Guía práctica LP II · sesión 13, pasos 2 a 13. Actividad autónoma LP II · sesión 13, partes A a F. Metafile de esbuild, build Angular, capturas del navegador, cabeceras de curl, salida de redis-cli, logs y métricas Actuator del laboratorio.',9.5)
add('Para repetir las pruebas: docs/s13-autonoma.md, tools/benchmark/README.md y tools/s13_autonoma.py. Evidencias por parte: docs/evidencias-s13-autonoma en el frontend.',9.5)

def decorate(c: canvas.Canvas, _doc):
    width,height=A4
    c.setFillColor(GOLD); c.rect(48,height-42,22,4,fill=1,stroke=0)
    c.setFillColor(BLUE); c.setFont('S13Bold',9); c.drawString(78,height-42,'PHARMASOFT')
    c.setFillColor(MUTED); c.setFont('S13',8.5)
    c.drawRightString(width-48,height-42,'LP II   /   ACTIVIDAD AUTÓNOMA S13')
    c.setStrokeColor(LINE); c.line(48,39,width-48,39)
    c.drawString(48,26,'Jatniel Jair Suarez Vigo  ·  Noviembre 2026')
    c.drawRightString(width-48,26,f'{c.getPageNumber():02}')

OUT.parent.mkdir(parents=True,exist_ok=True)
CLASSROOM.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=48,rightMargin=48,
                      topMargin=62,bottomMargin=52,title='PharmaSoft · Actividad Autónoma S13',
                      author='Jatniel Jair Suarez Vigo',pageCompression=1)
doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
shutil.copy2(OUT,CLASSROOM)
print(f'Informe: {OUT.name} | Copia: {CLASSROOM.name}')
