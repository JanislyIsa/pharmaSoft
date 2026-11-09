"""Comprobaciones S13 contra servicios locales reales. Evidencia sin tokens."""
import datetime
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT.parent / 'pharma-frontend'
OUT = FRONT / 'docs/evidencias-s13'
OUT.mkdir(parents=True, exist_ok=True)
DOCKER = r'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
COMPOSE = FRONT / 'deploy/docker-compose.yml'
RESULT = {'fecha': datetime.datetime.now().isoformat(), 'checks': [], 'requests': []}

def docker(*args):
    result = subprocess.run([DOCKER, *args], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr[-1000:])
    return result.stdout.strip()

def redis(*args):
    return docker('compose', '-f', str(COMPOSE), 'exec', '-T', 'redis', 'redis-cli', *args)

def request(path, token=None, data=None, method=None, base='http://localhost:8080', headers=None):
    hdr = dict(headers or {})
    if token:
        hdr['Authorization'] = 'Bearer ' + token
    if data is not None:
        hdr['Content-Type'] = 'application/json'
    req = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(),
                                 headers=hdr, method=method)
    start = time.perf_counter()
    try:
        response = urllib.request.urlopen(req, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read()
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    try:
        body = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        body = raw.decode('utf-8', errors='replace')
    record = {'method': req.get_method(), 'url': base + path, 'status': response.code,
              'duracionMs': elapsed, 'headers': dict(response.headers)}
    if not path.endswith('/auth/login'):
        record['body'] = body if not isinstance(body, str) else body[:300]
    RESULT['requests'].append(record)
    return response.code, body, record

def check(name, ok, detail):
    RESULT['checks'].append({'name': name, 'passed': bool(ok), 'detail': detail})
    print(('PASS ' if ok else 'FAIL ') + name, flush=True)
    save()

def save():
    (OUT / 'verificacion-api.json').write_text(json.dumps(RESULT, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    source = json.loads((ROOT / 'postman/PharmaSoft-S10-Seguridad.json').read_text(encoding='utf-8-sig'))
    variables = {v['key']: v.get('value', '') for v in source.get('variable', [])}
    def login(role):
        status, body, _ = request('/api/v1/auth/login', data={
            'username': variables['username' + role],
            'password': variables['password' + role] or (role + '2026*')})
        if status != 200:
            raise RuntimeError(f'Login {role} devolvió {status}; no se registra el cuerpo de autenticación.')
        return body['token']
    admin = login('Admin')
    seller = login('Vendedor')
    # Los tokens permanecen solo en memoria durante esta ejecución.
    status, body, _ = request('/actuator/health')
    check('12. Health público sin detalles', status == 200 and body['status'] == 'UP' and 'components' not in body, body)
    status, body, _ = request('/actuator/health', admin)
    check('Health admin con Oracle y Redis', status == 200 and all(k in body.get('components', {}) for k in ['db', 'redis']), body)
    status, body, _ = request('/actuator/metrics/http.server.requests', admin)
    check('Métricas admin autorizadas', status == 200 and body.get('name') == 'http.server.requests', body)
    status, body, _ = request('/actuator/metrics/http.server.requests', seller)
    check('13. Métricas vendedor bloqueadas', status == 403, {'status': status})
    redis('DEL', 'categorias::todas')
    s1, cats1, r1 = request('/api/v1/categorias', admin)
    s2, cats2, r2 = request('/api/v1/categorias', admin)
    exists, ttl = redis('EXISTS', 'categorias::todas'), int(redis('TTL', 'categorias::todas'))
    check('7. Categorías almacenadas con TTL', s1 == s2 == 200 and cats1 == cats2 and exists == '1' and 0 < ttl <= 600,
          {'primeraMs': r1['duracionMs'], 'segundaMs': r2['duracionMs'], 'exists': exists, 'ttl': ttl})
    status, hits, _ = request('/actuator/metrics/cache.gets?tag=name:categorias&tag=result:hit', admin)
    check('Aciertos Redis publicados en Actuator', status == 200 and any(m['value'] >= 1 for m in hits.get('measurements', [])), hits)
    stamp = datetime.datetime.now().strftime('%m%d%H%M%S')
    cat_payload = {'nombre': 'S13 Suarez ' + stamp, 'descripcion': 'Evidencia local de invalidacion S13', 'estado': True}
    status, category, _ = request('/api/v1/categorias', admin, cat_payload)
    after_write = redis('EXISTS', 'categorias::todas')
    s, cats, _ = request('/api/v1/categorias', admin)
    check('8. Crear categoría invalida y recarga', status == 201 and after_write == '0' and s == 200 and any(c['id'] == category['id'] for c in cats),
          {'categoriaId': category.get('id'), 'existsTrasCrear': after_write, 'existsTrasListar': redis('EXISTS', 'categorias::todas')})
    product_payload = {'nombre': 'Producto S13 Suarez ' + stamp, 'precio': 1.25, 'stock': 5, 'estado': True, 'categoriaId': category['id']}
    status, product, _ = request('/api/v1/productos', admin, product_payload)
    assert status == 201, 'No se pudo crear producto de prueba'
    pid = product['id']
    request(f'/api/v1/productos/{pid}', admin)
    request('/api/v1/productos?pagina=0&tamanio=10&ordenarPor=nombre&direccion=asc', admin)
    s, clients, _ = request('/api/v1/clientes?pagina=0&tamanio=100', admin)
    entries = clients.get('contenido', []) if isinstance(clients, dict) else clients
    client = next(c for c in entries if c.get('estado'))
    status, sale, _ = request('/api/v1/ventas', admin, {'clienteId': client['id'], 'detalles': [{'productoId': pid, 'cantidad': 1}]})
    exists_after_sale = redis('EXISTS', 'productos::id-' + str(pid))
    s, after_product, _ = request(f'/api/v1/productos/{pid}', admin)
    check('9. Venta invalida stock cacheado', status == 201 and exists_after_sale == '0' and after_product.get('stock') == 4,
          {'productoPruebaId': pid, 'ventaPruebaId': sale.get('id'), 'stockAntes': 5, 'stockDespues': after_product.get('stock'), 'cacheTrasVenta': exists_after_sale})
    # Prueba adicional de invalidación cruzada del nombre de categoría.
    cat_payload['nombre'] += ' Edit'
    status, _, _ = request('/api/v1/categorias/' + str(category['id']), admin, cat_payload, 'PUT')
    _, renamed, _ = request(f'/api/v1/productos/{pid}', admin)
    check('Actualizar categoría refresca nombre en producto', status == 200 and renamed.get('categoriaNombre') == cat_payload['nombre'], {'categoriaNombre': renamed.get('categoriaNombre')})
    _, _, log_request = request('/api/v1/categorias', admin)
    rid = next((v for k,v in log_request['headers'].items() if k.lower() == 'x-request-id'), '')
    log_path = ROOT / 'logs/pharma-backend.log'
    time.sleep(.2)
    logs = log_path.read_text(encoding='utf-8', errors='replace')
    matching = [line for line in logs.splitlines() if '[' + rid + ']' in line]
    check('11. X-Request-Id coincide con log', bool(rid) and bool(matching), {'requestId': rid, 'log': matching})
    try:
        docker('compose', '-f', str(COMPOSE), 'stop', 'redis')
        s, fallback, _ = request('/api/v1/categorias', admin)
        hs, health, _ = request('/actuator/health')
        warn = [line for line in log_path.read_text(encoding='utf-8', errors='replace').splitlines() if 'WARN' in line and 'Cache ' in line]
        check('10. Redis detenido: Oracle responde y health DOWN', s == 200 and hs == 503 and health.get('status') == 'DOWN' and bool(warn),
              {'categoriasStatus': s, 'healthStatus': hs, 'health': health, 'warn': warn[-2:]})
    finally:
        docker('compose', '-f', str(COMPOSE), 'start', 'redis')
        for _ in range(15):
            try:
                if redis('PING') == 'PONG':
                    break
            except Exception:
                pass
            time.sleep(1)
    s, body, _ = request('/actuator/health')
    check('Redis restaurado y health UP', s == 200 and body.get('status') == 'UP', body)
    all_logs = log_path.read_text(encoding='utf-8', errors='replace')
    check('14. Log de producción sin password ni Bearer', not re.search(r'password|Bearer', all_logs, re.I) and admin not in all_logs and seller not in all_logs, {'archivo': 'logs/pharma-backend.log', 'bytes': log_path.stat().st_size})
    s, html, _ = request('/index.html', base='http://localhost:8081')
    main = re.search(r'src="([^"]*main[^\"]+\.js)"', html).group(1)
    _, _, entry = request('/index.html', base='http://localhost:8081')
    _, _, asset = request('/' + main, base='http://localhost:8081', headers={'Accept-Encoding': 'gzip'})
    check('4. JS con caché anual e immutable', 'max-age=31536000' in str(asset['headers']) and 'immutable' in str(asset['headers']), asset['headers'])
    check('5. index.html siempre se revalida', 'no-cache' in str(entry['headers']), entry['headers'])
    check('Gzip habilitado para JavaScript', 'gzip' in str(asset['headers']), asset['headers'])
    s, html_route, _ = request('/productos', base='http://localhost:8081')
    check('6. F5 en /productos entrega Angular', s == 200 and html_route == html, {'status': s, 'indexCoincide': html_route == html})
    s, proxied, _ = request('/api/v1/categorias', admin, base='http://localhost:8081')
    check('Proxy Nginx hacia backend', s == 200 and isinstance(proxied, list), {'status': s})
    s, _, _ = request('/v3/api-docs', admin)
    check('Swagger desactivado en prod', s == 404, {'status': s})
    save()
    failures = [c['name'] for c in RESULT['checks'] if not c['passed']]
    print(f'Total: {len(RESULT["checks"])} comprobaciones; fallos: {len(failures)}.', flush=True)
    return len(failures)

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        RESULT['error'] = str(error)
        save()
        print(type(error).__name__ + ': ' + str(error), flush=True)
        raise SystemExit(1)
