"""Carga y medición de S14 contra el esquema local de desarrollo."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DOCKER = r'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
EVIDENCE = ROOT / 'docs/evidencias-s14'
COMPOSE = ROOT.parent / 'pharma-frontend/deploy/docker-compose.yml'


def sql(statement):
    config = (ROOT / 'src/main/resources/application-dev.yaml').read_text(encoding='utf-8')
    def setting(name):
        return re.search(r'^\s+' + name + r':\s*(.+)$', config, re.M).group(1).strip().strip('"\'')
    url = setting('url')
    if not re.search(r'@(//)?(localhost|127\.0\.0\.1):1522/', url):
        raise RuntimeError('La carga solo admite Oracle local en el puerto 1522.')
    service = url.rsplit('/', 1)[-1]
    password = setting('password').replace('"', '""')
    commands = (
        'whenever sqlerror exit sql.sqlcode rollback\n'
        'set heading off feedback off pagesize 0 linesize 32767 trimspool on serveroutput on\n'
        f'connect {setting("username")}/"{password}"@//localhost:1521/{service}\n'
        + statement + '\nexit\n'
    )
    result = subprocess.run([DOCKER, 'exec', '-i', 'oracle-local', 'sqlplus', '-S', '/nolog'],
                            input=commands, capture_output=True, text=True, timeout=150)
    if result.returncode:
        errors = [line for line in result.stdout.splitlines() if re.search(r'ORA-\d+|SP2-\d+', line)]
        raise RuntimeError('Oracle devolvió un error: ' + ' '.join(errors))
    return result.stdout.strip()


def save(name, value):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def request(path, token=None, payload=None):
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if payload is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request('http://localhost:8080' + path, headers=headers,
                                 data=None if payload is None else json.dumps(payload).encode())
    start = time.perf_counter()
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read()
    value = json.loads(raw)
    record = {
        'path': path, 'status': response.status,
        'milliseconds': round((time.perf_counter() - start) * 1000, 3),
        'bodyBytes': len(raw), 'requestId': response.headers.get('X-Request-Id'),
    }
    if isinstance(value, dict) and 'contenido' in value:
        record.update({key: value[key] for key in ('pagina', 'tamanio', 'totalElementos', 'totalPaginas', 'ultima')})
        record['filas'] = len(value['contenido'])
        record['ids'] = [row['id'] for row in value['contenido']]
    return value, record


def inspect_schema():
    print(sql("""
        select table_name || '.' || column_name || ' ' || data_type
        from user_tab_columns
        where table_name in ('PRODUCTOS','CLIENTES','VENTAS')
        and column_name in ('ID_CATEGORIA','CATEGORIA_ID','ESTADO','CREADO_POR','FECHA_CREACION')
        order by table_name, column_name;
        select 'PRODUCTOS=' || count(*) from productos;
        select 'VENTAS=' || count(*) from ventas;
    """))


def load():
    statement = (ROOT / 'docs/sql/volumen_pruebas.sql').read_text(encoding='utf-8')
    result = sql(statement)
    save('02-volumen.json', {'date': dt.datetime.now().isoformat(), 'sqlResult': result,
                            'script': 'docs/sql/volumen_pruebas.sql'})
    print(result)


def measure(stage):
    import getpass
    import os
    password = os.environ.get('S14_ADMIN_PASSWORD') or getpass.getpass('Contraseña local del administrador: ')
    login, status = request('/api/v1/auth/login', payload={'username': 'admin', 'password': password})
    if status['status'] != 200:
        raise RuntimeError('No se pudo iniciar sesión para medir.')
    token = login['token']
    clear = subprocess.run([DOCKER, 'compose', '-f', str(COMPOSE), 'exec', '-T', 'redis',
                            'redis-cli', '--scan', '--pattern', 'productos::*'],
                           capture_output=True, text=True, check=True)
    for key in clear.stdout.splitlines():
        subprocess.run([DOCKER, 'compose', '-f', str(COMPOSE), 'exec', '-T', 'redis',
                        'redis-cli', 'UNLINK', key], capture_output=True, check=True)
    paths = ['/api/v1/productos?pagina=0&tamanio=20',
             '/api/v1/productos?pagina=0&tamanio=100',
             '/api/v1/productos?pagina=249&tamanio=20',
             '/api/v1/productos?pagina=0&tamanio=500',
             '/api/v1/productos?pagina=0&tamanio=20&ordenarPor=campoInvalido',
             '/api/v1/ventas/buscar?desde=2026-11-01&hasta=2026-11-12&pagina=0']
    records = []
    for path in paths:
        _, record = request(path, token)
        records.append(record)
    _, first = request('/api/v1/productos?pagina=0&tamanio=20', token)
    last_page = max(0, first['totalPaginas'] - 1)
    _, last = request(f'/api/v1/productos?pagina={last_page}&tamanio=20', token)
    records.append(last)
    save(f'02-mediciones-{stage}.json', {'stage': stage, 'records': records})
    if stage == 'despues':
        assert records[3]['status'] == 409 and records[4]['status'] == 409
        assert records[0]['filas'] == 20 and records[1]['filas'] == 100
        assert records[-1]['ultima'] and records[5]['status'] == 200
    for record in records:
        print(record['status'], record['milliseconds'], 'ms', record['bodyBytes'], 'bytes', record['path'])


def capture_sql():
    log = (ROOT / '.local/s14-dev.log').read_text(encoding='utf-8', errors='replace')
    statements = re.findall(r'(?ms)^    select\b.*?(?=^\d{4}-|\Z)', log)
    page = next(statement for statement in statements if 'productos' in statement and 'fetch' in statement)
    count = next(statement for statement in statements if 'productos' in statement and 'count(' in statement)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / '02-sql-paginacion.txt').write_text(
        'Consulta paginada de Hibernate\n' + page.strip()
        + '\n\nConsulta del total\n' + count.strip() + '\n', encoding='utf-8')
    print('OFFSET, FETCH y COUNT de productos guardados.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inspect', 'load', 'measure', 'sql'])
    parser.add_argument('--stage', default='despues', choices=['antes', 'despues'])
    args = parser.parse_args()
    if args.action == 'inspect':
        inspect_schema()
    elif args.action == 'load':
        load()
    elif args.action == 'sql':
        capture_sql()
    else:
        measure(args.stage)
