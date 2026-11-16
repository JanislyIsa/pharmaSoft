"""Pruebas reales S13 autónoma. Solo crea/modifica fixtures propios AA S13 Auto."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
FRONT=ROOT.parent/'pharma-frontend'
OUT=FRONT/'docs/evidencias-s13-autonoma'
DOCKER=r'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
COMPOSE=FRONT/'deploy/docker-compose.yml'

def save(part,name,data):
    folder=OUT/part;folder.mkdir(parents=True,exist_ok=True)
    (folder/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def docker(*args):
    p=subprocess.run([DOCKER,*map(str,args)],capture_output=True,text=True,timeout=50)
    if p.returncode:raise RuntimeError(p.stderr[-700:])
    return p.stdout.strip()

def redis(*args,db=0):
    return docker('compose','-f',COMPOSE,'exec','-T','redis','redis-cli','-n',db,*args)

def http(path,token=None,data=None,method=None,port=8080):
    headers={'Accept':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    if data is not None:headers['Content-Type']='application/json'
    req=urllib.request.Request(f'http://localhost:{port}'+path,data=None if data is None else json.dumps(data).encode(),headers=headers,method=method)
    start=time.perf_counter()
    try:r=urllib.request.urlopen(req,timeout=20)
    except urllib.error.HTTPError as ex:r=ex
    raw=r.read();ms=round((time.perf_counter()-start)*1000,3)
    try:body=json.loads(raw)
    except ValueError:body=raw.decode(errors='replace')
    return r.code,body,{'status':r.code,'durationMs':ms,'requestId':r.headers.get('X-Request-Id'),'headers':dict(r.headers)}

def login(role='Admin',port=8080):
    key=f'S13_{role.upper()}'
    username=os.environ.get(key+'_USER',role.lower())
    password=os.environ.get(key+'_PASSWORD')
    if not password:
        from getpass import getpass
        password=getpass(f'Contraseña local de {username}: ')
    s,b,_=http('/api/v1/auth/login',data={'username':username,'password':password},port=port)
    assert s==200,f'Login {role}: HTTP {s}'
    return b['token']

def metric(token,name,result):
    query=urllib.parse.urlencode([('tag','name:'+name),('tag','result:'+result)])
    s,b,_=http('/actuator/metrics/cache.gets?'+query,token)
    assert s==200,(s,b)
    return sum(x['value'] for x in b['measurements'])

def caches():
    token=login();result={'fecha':dt.datetime.now().isoformat(),'series':{}}
    for name,path,key in [('categorias','/api/v1/categorias','categorias::todas'),('productos','/api/v1/productos?pagina=0&tamanio=10&ordenarPor=nombre&direccion=asc','productos::0-10-nombre: ASC')]:
        redis('DEL',key)
        before={k:metric(token,name,k) for k in ['hit','miss']}
        calls=[]
        for i in range(20):
            s,b,r=http(path,token);assert s==200
            calls.append({'numero':i+1,**{k:r[k] for k in ['status','durationMs','requestId']}})
        after={k:metric(token,name,k) for k in ['hit','miss']}
        hits=after['hit']-before['hit'];misses=after['miss']-before['miss']
        assert hits==19 and misses==1,(name,hits,misses)
        result['series'][name]={'before':before,'after':after,'hits':hits,'misses':misses,'hitRatePercent':100*hits/(hits+misses),
          'firstMissMs':calls[0]['durationMs'],'meanHitsMs':round(statistics.mean(c['durationMs'] for c in calls[1:]),3),'calls':calls}
        print(f'{name}: {hits} aciertos, {misses} fallo; tasa 95%; tiempo frío y media guardados.',flush=True)
    save('C','C-aciertos-20x2.json',result)

def ttl():
    token=login(port=8082);redis('DEL','categorias::todas',db=1)
    s,_,_=http('/api/v1/categorias',token,port=8082);assert s==200
    rows=[];start=time.monotonic()
    while time.monotonic()-start<72:
        elapsed=round(time.monotonic()-start,1);value=int(redis('TTL','categorias::todas',db=1));exists=int(redis('EXISTS','categorias::todas',db=1))
        rows.append({'seconds':elapsed,'ttl':value,'exists':exists});save('C','C-ttl-1-minuto.json',{'instancia':'prod temporal 8082, Redis DB 1','configuracion':'--spring.cache.redis.time-to-live=1m','muestras':rows})
        print(f'TTL: t={elapsed}s, ttl={value}, exists={exists}',flush=True)
        if exists==0:break
        time.sleep(10)
    assert rows[0]['ttl'] in [59,60] and rows[-1]['exists']==0,rows
    admin=login();redis('DEL','categorias::todas');http('/api/v1/categorias',admin)
    normal=int(redis('TTL','categorias::todas'))
    assert normal>590
    save('C','C-ttl-restaurado.json',{'instanciaNormal':8080,'redisDB':0,'ttlSeconds':normal,'configFuente':'${CACHE_TTL:10m}'})
    print('TTL de la instancia normal comprobado de nuevo: 10 minutos.',flush=True)

def matrix():
    token=login();stamp=dt.datetime.now().strftime('%m%d%H%M%S');cases=[]
    http('/api/v1/categorias',token)
    cat={'nombre':'AA S13 Auto Categoria '+stamp,'descripcion':'Fixture autónoma S13','estado':True}
    s,c,_=http('/api/v1/categorias',token,cat);assert s==201
    missing=redis('EXISTS','categorias::todas');_,cats,_=http('/api/v1/categorias',token)
    ok=missing=='0' and any(x['id']==c['id'] for x in cats);assert ok
    cases.append({'id':'C-01','passed':ok,'categoriaId':c['id'],'cacheAfterWrite':missing,'nombreVisible':cat['nombre']})
    prod={'nombre':'AA S13 Auto Producto '+stamp,'precio':3.25,'stock':8,'estado':True,'categoriaId':c['id']}
    s,p,_=http('/api/v1/productos',token,prod);assert s==201
    query='/api/v1/productos?pagina=0&tamanio=10&ordenarPor=nombre&direccion=asc'
    http(query,token);http('/api/v1/productos/'+str(p['id']),token)
    cat['nombre']+=' Edit'
    s,_,_=http('/api/v1/categorias/'+str(c['id']),token,cat,'PUT');assert s==200
    _,products,_=http(query,token);row=next(x for x in products['contenido'] if x['id']==p['id'])
    assert row['categoriaNombre']==cat['nombre']
    cases.append({'id':'C-02','passed':True,'productoId':p['id'],'categoriaNombre':row['categoriaNombre']})
    prod['precio']=4.50
    s,_,_=http('/api/v1/productos/'+str(p['id']),token,prod,'PUT');assert s==200
    _,detail,_=http('/api/v1/productos/'+str(p['id']),token);_,products,_=http(query,token)
    row=next(x for x in products['contenido'] if x['id']==p['id'])
    assert detail['precio']==row['precio']==4.5
    cases.append({'id':'C-03','passed':True,'precioAntes':3.25,'precioDetalle':detail['precio'],'precioLista':row['precio']})
    empty={'nombre':'AA S13 Auto Eliminar '+stamp,'descripcion':'Fixture temporal sin productos','estado':True}
    s,emptycat,_=http('/api/v1/categorias',token,empty);assert s==201
    http('/api/v1/categorias',token)
    # Solo se borra la categoría acabada de crear aquí, nunca una categoría existente.
    assert emptycat['nombre']==empty['nombre'] and emptycat['id']!=c['id']
    s,_,_=http('/api/v1/categorias/'+str(emptycat['id']),token,method='DELETE');assert s==204
    missing=redis('EXISTS','categorias::todas');_,cats,_=http('/api/v1/categorias',token)
    assert missing=='0' and not any(x['id']==emptycat['id'] for x in cats)
    cases.append({'id':'C-05','passed':True,'categoriaTemporalEliminadaId':emptycat['id'],'yaNoAparece':True,'cacheAfterDelete':missing})
    _,clients,_=http('/api/v1/clientes?pagina=0&tamanio=100',token)
    clients=clients.get('contenido',[]) if isinstance(clients,dict) else clients
    client=next(x for x in clients if x['estado'])
    state={'categoriaId':c['id'],'productoId':p['id'],'productoNombre':prod['nombre'],'clienteId':client['id'],
           'clienteBusqueda':client['nombres'],'stockAntesVenta':8,'precio':4.5,'queryLista':query}
    save('C','C-fixture.json',state);save('C','C-matriz.json',cases)
    print('C-01, C-02, C-03 y C-05 aprobados. Fixture preparado para venta desde la SPA.',flush=True)

def after_sale(sale_id):
    token=login();fixture=json.loads((OUT/'C/C-fixture.json').read_text(encoding='utf-8'))
    _,products,_=http(fixture['queryLista'],token)
    row=next(x for x in products['contenido'] if x['id']==fixture['productoId'])
    assert row['stock']==fixture['stockAntesVenta']-1
    cases=json.loads((OUT/'C/C-matriz.json').read_text(encoding='utf-8'))
    cases.append({'id':'C-04','passed':True,'ventaId':int(sale_id),'productoId':row['id'],'stockAntes':8,'stockListaDespues':row['stock'],'ventaDesde':'SPA'})
    save('C','C-matriz.json',cases)
    _,sale,_=http('/api/v1/ventas/'+str(sale_id),token)
    assert sale['detalles'][0]['productoId']==fixture['productoId']
    print('C-04 aprobado: stock de 8 a 7 tras venta desde la SPA.',flush=True)

def down():
    docker('compose','-f',COMPOSE,'stop','redis')
    token=login();s,products,r=http('/api/v1/productos?pagina=0',token)
    assert s==200
    a,anon,ar=http('/actuator/health');b,admin,br=http('/actuator/health',token)
    assert a==b==503 and anon['status']==admin['status']=='DOWN'
    save('C','C-06-redis-down.json',{'productos':r,'healthAnon':{'status':a,'body':anon},'healthAdmin':{'status':b,'body':admin}})
    print('C-06: productos 200 desde Oracle; health sin token y admin DOWN. Redis queda detenido para captura SPA.',flush=True)

def up():
    docker('compose','-f',COMPOSE,'start','redis')
    for _ in range(20):
        try:
            if redis('PING')=='PONG':break
        except Exception:pass
        time.sleep(1)
    token=login()
    for _ in range(20):
        a,anon,_=http('/actuator/health')
        b,admin,_=http('/actuator/health',token)
        if a==b==200 and anon['status']==admin['status']=='UP':
            break
        time.sleep(1)
    assert a==b==200 and anon['status']==admin['status']=='UP'
    save('D','D-health-up.json',{'anon':anon,'admin':admin})
    print('Redis restaurado; ambos health UP.',flush=True)

def audit():
    token=login();seller=login('Vendedor');s,_,_=http('/actuator/metrics',seller);assert s==403
    _,clients,_=http('/api/v1/clientes?pagina=0&tamanio=100',token)
    clients=clients.get('contenido',[]) if isinstance(clients,dict) else clients
    dnis=[str(c['dni']) for c in clients if c.get('dni')]
    logs=(ROOT/'logs/pharma-backend.log').read_text(encoding='utf-8',errors='replace')
    secret=(ROOT/'.local/s13-jwt.key').read_text().strip()
    dev=(ROOT/'src/main/resources/application-dev.yaml').read_text(encoding='utf-8')
    dbpassword=re.search(r'^\s+password:\s*(.+)$',dev,re.M).group(1).strip().strip('\"\'')
    findings={'patronPasswordBearerSecret':len(re.findall(r'password|Bearer |secret',logs,re.I)),
              'claveJwtCompleta':secret in logs,'tokensCompletos':token in logs or seller in logs,
              'passwordDBCompleto':dbpassword in logs,'dniClientesCompletos':sum(d in logs for d in dnis)}
    assert not any(findings.values()),findings
    s,metrics,_=http('/actuator/metrics/http.server.requests?tag=uri%3A%2Fapi%2Fv1%2Fventas',token)
    assert s==200
    save('D','D-auditoria-y-metricas.json',{'audit':findings,'logBytes':len(logs.encode()),'dniValoresComprobados':len(dnis),'metricsVentas':metrics})
    s,error,r=http('/api/v1/productos/999999999',token)
    assert s==404 and error.get('requestId')==r['requestId']
    save('D','D-error-api.json',{'response':error,'headers':r['headers'],'matched':True})
    print('Auditoría aprobada; métricas de ventas y requestId de error guardados.',flush=True)

def deployment(stage):
    build=FRONT/'dist/pharma-frontend'
    browser=build/'browser'
    stats=json.loads((build/'browser-stats.json').read_text(encoding='utf-8'))
    entries={Path(name).name: data.get('entryPoint','') for name,data in stats['outputs'].items()}
    sales=next(name for name,path in entries.items() if path.endswith('/venta-list.ts'))
    product=next(name for name,path in entries.items() if path.endswith('/producto-list.ts'))
    index=(browser/'index.html').read_text(encoding='utf-8')
    paths=['/index.html','/'+re.search(r'main-[\w-]+\.js',index).group(),
           '/'+sales,'/'+re.search(r'styles-[\w-]+\.css',index).group(),'/api/v1/categorias']
    container=docker('compose','-f',COMPOSE,'ps','-q','web')
    started=docker('inspect','--format','{{.State.StartedAt}}',container)
    token=login()
    headers={}
    for path in paths:
        status,_,record=http(path,token if path.startswith('/api/') else None,port=8081)
        assert status==200,(path,status)
        headers[path]={k.lower():v for k,v in record['headers'].items()
                       if k.lower() in {'cache-control','etag','last-modified','content-type','x-request-id'}}
    assert headers[paths[0]]['cache-control']=='no-cache'
    assert all(headers[p]['cache-control']=='public, max-age=31536000, immutable' for p in paths[1:4])
    assert 'no-store' in headers[paths[-1]]['cache-control']
    save('B',f'B-manifiesto-{stage}.json',{'containerId':container,'startedAt':started,
         'headers':headers,'main':paths[1][1:],'sales':sales,'product':product,'styles':paths[3][1:],
         'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in browser.iterdir()
                  if f.is_file() and (f.suffix in {'.js','.css'} and f.name!='browser-evidence.js')}})
    print(f'Cabeceras Nginx validadas; manifiesto {stage} guardado.',flush=True)

def sale_trace():
    rec=json.loads((OUT/'D/D-venta-post.json').read_text(encoding='utf-8'))
    req=rec['requestId']
    assert re.fullmatch(r'[a-f0-9]{8}',req)
    logs=(ROOT/'logs/pharma-backend.log').read_text(encoding='utf-8',errors='replace')
    lines=[line for line in logs.splitlines() if f'[{req}]' in line]
    assert any('POST /api/v1/ventas -> 201' in line for line in lines)
    assert any('ventaId='+str(rec['entityId']) in line for line in lines)
    save('D','D-venta-traza.json',{'request':rec,'logLines':lines})
    print(f'Venta {rec["entityId"]}: {len(lines)} líneas correlacionadas con {req}.',flush=True)

def head_check():
    before=json.loads((OUT/'B/B-manifiesto-antes.json').read_text(encoding='utf-8'))
    after=json.loads((OUT/'B/B-manifiesto-despues.json').read_text(encoding='utf-8'))
    assert before['containerId']==after['containerId'] and before['startedAt']==after['startedAt']
    token=login()
    data={}
    for path in after['headers']:
        config=f'header = "Authorization: Bearer {token}"\n' if path.startswith('/api/') else ''
        result=subprocess.run(['curl.exe','-sS','-I','--config','-',f'http://localhost:8081{path}'],
                              input=config,capture_output=True,text=True,check=True,timeout=15)
        headers=[line for line in result.stdout.splitlines()
                 if line.lower().startswith(('http/','cache-control:','etag:','last-modified:'))]
        assert headers[0].split()[1]=='200',(path,headers)
        data[path]=headers
    etag=next(line.split(':',1)[1].strip() for line in data['/index.html']
              if line.lower().startswith('etag:'))
    result=subprocess.run(['curl.exe','-sS','-I','-H',f'If-None-Match: {etag}',
                           'http://localhost:8081/index.html'],capture_output=True,text=True,check=True,timeout=15)
    conditional=result.stdout.splitlines()[0]
    assert conditional.split()[1]=='304',conditional
    save('B','B-curl-head.json',{'headers':data,'indexConditional':conditional,'sameContainer':True})
    print('curl -I: cinco recursos HTTP 200 y validación condicional de index HTTP 304.',flush=True)

if __name__=='__main__':
    actions={'caches':caches,'ttl':ttl,'matrix':matrix,'after-sale':lambda:after_sale(int(sys.argv[2])),
             'down':down,'up':up,'audit':audit,'deploy':lambda:deployment(sys.argv[2]),'sale-trace':sale_trace,
             'head':head_check}
    try:actions[sys.argv[1]]()
    except Exception as error:
        print(type(error).__name__+': '+str(error),flush=True);raise SystemExit(1)
