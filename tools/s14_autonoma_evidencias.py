"""Consolida evidencia real S14 sin exportar credenciales ni tráfico autenticado."""
import base64
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont
from s14_local import sql

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT.parent / 'pharma-frontend'
OUT = ROOT / 'docs/evidencias/s14-estabilizacion'
OUT.mkdir(parents=True, exist_ok=True)

def guardar(nombre, valor):
    (OUT/nombre).write_text(json.dumps(valor, ensure_ascii=False, indent=2), encoding='utf-8')

def tarjeta(nombre, titulo, texto):
    fuente=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
    lineas=[]
    for linea in texto.splitlines(): lineas.extend(textwrap.wrap(linea,105,replace_whitespace=False) or [''])
    im=Image.new('RGB',(1480,125+34*len(lineas)), '#f5f7fb');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1480,78),fill='#12315d');d.text((30,24),titulo,font=fuente,fill='white')
    for i,linea in enumerate(lineas):d.text((30,100+34*i),linea,font=fuente,fill='#142c4d')
    im.save(OUT/nombre)

def main():
    r=json.loads((FRONT/'test-results/resultados.json').read_text(encoding='utf-8'))
    assert r['stats']['expected']==42 and r['stats']['unexpected']==0 and r['stats']['flaky']==0
    casos=[]
    def recorrer(suites):
        for s in suites:
            for spec in s.get('specs',[]):
                for test in spec['tests']:
                    for resultado in test['results']:
                        casos.append({'prueba':spec['title'],'repeticion':test.get('repeatEachIndex',0)+1,
                          'estado':resultado['status'],'duracionMs':resultado['duration'],'retry':resultado['retry']})
            recorrer(s.get('suites',[]))
    recorrer(r['suites']); assert len(casos)==42 and all(c['retry']==0 for c in casos)
    # La API JSON de Playwright incluye repeatEachIndex en tests en versiones actuales.
    # Si no lo expone, el orden por título determina cada repetición sin inferir resultados.
    indices={}
    for c in casos:
        indices[c['prueba']]=indices.get(c['prueba'],0)+1
        c['repeticion']=indices[c['prueba']]
    versiones={n:subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip() for n,p in [('backend',ROOT),('frontend',FRONT)]}
    guardar('playwright-resumen.json',{'fecha':dt.datetime.now().astimezone().isoformat(),'versiones':versiones,'stats':r['stats'],'workers':1,'retries':0,'casos':casos})
    shutil.copytree(FRONT/'playwright-report',OUT/'playwright-report',dirs_exist_ok=True)
    foto=sorted((FRONT/'test-results').glob('**/auditoria-integrada.png'),key=lambda p:p.stat().st_mtime)[-1]
    shutil.copy2(foto,OUT/'auditoria-spa.png')
    guardar('diagnosticos.json',{'entorno':{'fecha':'2026-11-15','resultado':'42 fallos de arranque; Chromium no instalado','solucion':'playwright install chromium'},
        'selector':{'resultado':'39 aprobadas, 3 fallidas','causa':'selectOption esperaba la etiqueta exacta Acción','trace':'locator.selectOption -> internal:label="Acción"s; timeout 60000 ms','correccion':'aria-label Acción; frontend 5809bc4'},
        'verificacionPosterior':{'aprobadas':42,'fallidas':0,'flaky':0,'retries':0},'nota':'No se publican trazas con tráfico autenticado.'})
    summary=next((ROOT/'.local/s14-postman-output').glob('*summary.yaml')).read_text(encoding='utf-8')
    ejec=next((ROOT/'.local/s14-postman-output').glob('*executions.yaml')).read_text(encoding='utf-8')
    solicitudes=[]
    for bloque in ejec.split('\n---\n')[1:]:
        nombre=re.search(r'^  fullName: (.+)$',bloque,re.M)
        codigo=re.search(r'^  code: (\d+)$',bloque,re.M)
        if nombre and codigo:solicitudes.append({'nombre':nombre.group(1),'http':int(codigo.group(1))})
    assert len(solicitudes)==18 and {200,201,400,401,403,404,409} <= {x['http'] for x in solicitudes}
    assert re.search(r'tests:\s+executed: 26\s+failed: 0',summary)
    guardar('postman-resumen.json',{'fecha':'2026-11-15','cli':'Postman CLI 1.90.0','solicitudes':solicitudes,'assertions':26,'failed':0,'durationMs':int(re.search(r'  durationMs: (\d+)',summary).group(1)), 'exitCode':0,'destino':'http://localhost:8080/api/v1'})
    manual=json.loads((OUT/'recorridos-manuales.json').read_text(encoding='utf-8'))
    venta=manual['recorridos'][0]['ventaId']
    fila=sql(f"select json_object('ventaId' value v.id,'creadoPor' value v.creado_por,'total' value v.total,'accion' value a.accion,'usuario' value a.usuario,'requestId' value a.request_id,'eventoId' value a.id) from ventas v join auditoria_eventos a on a.entidad_id=v.id and a.accion='VENTA_REGISTRADA' where v.id={int(venta)};")
    datos=json.loads(fila)
    # El perfil dev incluye MDC en la consola; prod también lo incluye en el archivo rotativo.
    logs=[l for l in (ROOT/'.local/s13-dev-8080-console.log').read_text(encoding='utf-8').splitlines() if datos['requestId'] in l]
    assert logs and datos['creadoPor']==datos['usuario']=='vendedor'
    guardar('trazabilidad.json',{'fecha':dt.datetime.now().astimezone().isoformat(),'consulta':f'ventas JOIN auditoria_eventos WHERE ventas.id={venta}', 'resultado':datos,'log':logs})
    tarjeta('trazabilidad-bd.png','Oracle local - venta y bitácora (consulta real)',json.dumps(datos,ensure_ascii=False,indent=2))
    tarjeta('trazabilidad-log.png','Log real del backend - mismo requestId','\n'.join(logs))
    tarjeta('postman-resultados.png','Postman CLI - 18 solicitudes y 26 comprobaciones aprobadas','\n'.join(f"HTTP {s['http']}  {s['nombre']}" for s in solicitudes))
    tarjeta('playwright-resultados.png','Playwright - 14 casos x 3 = 42 aprobadas',f"Inicio UTC: {r['stats']['startTime']}\nDuración total: {r['stats']['duration']/1000:.2f} s\nFallidas: 0 | Flaky: 0 | Reintentos: 0 | Workers: 1\nBackend: {versiones['backend'][:7]} | Frontend: {versiones['frontend'][:7]}")
    conteos=sql("select 'PRODUCTOS='||count(*) from productos;\nselect 'VENTAS='||count(*) from ventas;\nselect accion||'='||count(*) from auditoria_eventos group by accion order by accion;")
    guardar('volumen.json',{'fecha':dt.datetime.now().astimezone().isoformat(),'resultado':conteos})
    validacion=[l for l in (ROOT/'.local/s14-autonoma-maven-verificado.log').read_text(encoding='utf-8').splitlines() if 'Tests run:' in l or 'BUILD SUCCESS' in l]
    (OUT/'backend-validacion.txt').write_text('\n'.join(validacion),encoding='utf-8')
    # Solo capturas conocidas sin contraseñas ni JWT visibles; conservar procedencia.
    grupos={
      'u2-spa-segura':[(FRONT/'docs/evidencias-autonoma/X-01_comprobante-servidor-venta-92.png','comprobante-s11.png'),(FRONT/'docs/evidencias-autonoma/X-01_stock-final-amoxicilina-42.png','stock-s11.png')],
      's13-optimizacion':[(FRONT/'docs/evidencias-s13-autonoma/A/A-top5.csv','A-top5.csv'),(FRONT/'docs/evidencias-s13-autonoma/A/A-analyzer.png','A-analyzer.png'),(FRONT/'docs/evidencias-s13-autonoma/C/C-matriz.json','C-matriz.json'),(FRONT/'docs/evidencias-s13-autonoma/D/D-venta-registrada.png','D-venta-registrada.png')]}
    for grupo,archivos in grupos.items():
        carpeta=ROOT/'docs/evidencias'/grupo;carpeta.mkdir(exist_ok=True)
        origen=[]
        for fuente,nombre in archivos:
            if fuente.exists():shutil.copy2(fuente,carpeta/nombre);origen.append(f'- [{nombre}]({nombre}): copia conservada de frontend/{fuente.relative_to(FRONT).as_posix()}.')
        (carpeta/'README.md').write_text('# Evidencias conservadas\n\n'+ '\n'.join(origen)+'\n\nSe conserva la fecha y contenido original; no son capturas nuevas del 15/11.\n',encoding='utf-8')
    u1=ROOT/'docs/evidencias/u1-backend';u1.mkdir(exist_ok=True)
    shutil.copy2(OUT/'postman-resultados.png',u1/'validacion-actual-api.png')
    (u1/'README.md').write_text('# Backend\n\n[Validación actual de la API](validacion-actual-api.png), realizada el 15/11/2026.\n\nNo se localizaron capturas originales identificadas de las sesiones 1 a 5. Esta reconstrucción actual no se presenta como evidencia histórica. Añadir aquí esas capturas originales si el docente las exige.\n',encoding='utf-8')
    print('Evidencias: Playwright 42/42, Postman 26/26 y venta trazada',venta,datos['requestId'])

if __name__=='__main__':main()
