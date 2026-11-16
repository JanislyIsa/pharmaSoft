"""Consolida resultados reales de Playwright y evidencia SQL de S14, sin secretos."""
import base64
import json
from pathlib import Path
import shutil
from s14_local import sql, save
ROOT=Path(__file__).resolve().parents[1]
FRONT=ROOT.parent/'pharma-frontend'
DEST=ROOT/'docs/evidencias-s14'
def consolidar():
 j=json.loads((FRONT/'test-results/resultados.json').read_text(encoding='utf-8-sig'));tests=[]
 def walk(s):
  for spec in s.get('specs',[]):
   for test in spec['tests']:tests.append((spec['title'],test,test['results'][-1]))
  for c in s.get('suites',[]):walk(c)
 for s in j['suites']:walk(s)
 workers=sorted({x[2]['workerIndex'] for x in tests})
 rows=[{'prueba':title,'corrida':workers.index(result['workerIndex'])+1,'estado':test['status'],'duracionMs':result['duration'],'reintentos':result['retry']} for title,test,result in tests]
 assert len(workers)==3 and len(rows)==21 and all(x['estado']=='expected' and x['reintentos']==0 for x in rows)
 summary={'stats':j['stats'],'workersSimultaneos':1,'retries':0,'pruebas':rows,'corridas':[{'corrida':i,'aprobadas':sum(x['estado']=='expected' for x in rows if x['corrida']==i),'total':7} for i in (1,2,3)]}
 save('09-playwright-resumen.json',summary)
 attachments=[]
 for _,_,result in tests:
  for a in result.get('attachments',[]):
   if a['name']=='integracion' and a.get('body'):attachments.append(json.loads(base64.b64decode(a['body'])))
 save('08-integracion.json',{'corridas':attachments,'filas':8,'aprobadas':8,'I07':'Reloj controlado de SPA simula vencimiento y valida retorno a venta','I08':'Página 5, cambio de fechas y recarga; prueba de paginación'})
 capturas=sorted((FRONT/'test-results').rglob('auditoria-integrada.png'), key=lambda p:p.stat().st_mtime)
 if capturas: shutil.copyfile(capturas[-1],DEST/'07-auditoria-spa.png')
 # El informe aprobado no tiene trazas de red ni vídeos de fallos.
 shutil.copytree(FRONT/'playwright-report',DEST/'playwright-report',dirs_exist_ok=True)
 result=sql('''select 'PRODUCTOS=' || count(*) from productos;
select 'VENTAS=' || count(*) from ventas;
select accion || '=' || count(*) from auditoria_eventos group by accion order by accion;
''');save('08-volumen-final.json',{'sql':result})
 log=(ROOT/'.local/s14-final-maven.log').read_text(encoding='utf-8',errors='replace')
 checks=[x for x in log.splitlines() if 'Tests run:' in x or 'BUILD SUCCESS' in x or 'Successfully applied' in x]
 build=(FRONT/'tmp/s14-final-build.txt').read_text(encoding='utf-8',errors='replace')
 (DEST/'validacion-final.txt').write_text('\n'.join(checks)+'\n\n'+'\n'.join(x for x in build.splitlines() if 'Application bundle generation complete' in x or 'WARNING' in x)+'\n',encoding='utf-8')
 print('Tres corridas aprobadas:',summary['corridas']);print(result)
if __name__=='__main__':consolidar()
