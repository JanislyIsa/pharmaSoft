"""Arranque local de S13. No imprime ni versiona secretos."""
import base64
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'
LOCAL.mkdir(exist_ok=True)

def suffix(profile, port):
    return profile if port == (8080 if profile == 'prod' else 8082) else f'{profile}-{port}'

def stop(profile='prod', port=8080):
    record = LOCAL / f's13-{suffix(profile, port)}-pid.json'
    if not record.exists():
        print('No hay registro de proceso propio; no se detiene ningún proceso.')
        return True
    pid = int(json.loads(record.read_text())['pid'])
    jar = str(ROOT / 'target/PharmaBackend-0.0.1-SNAPSHOT.jar').replace("'", "''")
    command = (f"$taskProcess = Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}'; "
               f"if (!$taskProcess) {{ exit 0 }}; "
               f"if ($taskProcess.CommandLine.Contains('{jar}') -and "
               f"$taskProcess.CommandLine.Contains('--server.port={port}')) "
               f"{{ Stop-Process -Id {pid}; Write-Output 'Backend propio detenido.' }} "
               "else { Write-Error 'PID no corresponde al proceso registrado'; exit 1 }")
    return subprocess.run(['powershell.exe', '-NoProfile', '-Command', command]).returncode == 0

def start(profile='prod', port=8080, extra=None):
    try:
        with urllib.request.urlopen(f'http://localhost:{port}/actuator/health', timeout=3) as response:
            if response.status == 200:
                print(f'El servicio del puerto {port} ya está activo y saludable.')
                return True
    except Exception:
        pass
    dev = (ROOT / 'src/main/resources/application-dev.yaml').read_text(encoding='utf-8')
    def value(name):
        return re.search(r'^\s+' + name + r':\s*(.+)$', dev, re.M).group(1).strip().strip('\"\'')
    key = LOCAL / 's13-jwt.key'
    if not key.exists():
        key.write_text(base64.b64encode(secrets.token_bytes(48)).decode(), encoding='ascii')
    env = os.environ.copy()
    env.update(SPRING_PROFILES_ACTIVE=profile, SERVER_PORT=str(port),
               DB_URL=value('url'), DB_USERNAME=value('username'), DB_PASSWORD=value('password'),
               JWT_SECRET=key.read_text().strip(), FRONTEND_ORIGINS='http://localhost:8081')
    java = Path.home() / '.jdks/ms-21.0.11/bin/java.exe'
    jar = ROOT / 'target/PharmaBackend-0.0.1-SNAPSHOT.jar'
    log = LOCAL / f's13-{suffix(profile, port)}-console.log'
    with log.open('w', encoding='utf-8') as output:
        child = subprocess.Popen([str(java), '-jar', str(jar), f'--server.port={port}', *(extra or [])],
                                 cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    (LOCAL / f's13-{suffix(profile, port)}-pid.json').write_text(json.dumps({'pid': child.pid, 'port': port}), encoding='utf-8')
    print(f'Backend {profile} iniciado, PID {child.pid}; esperando puerto {port}.', flush=True)
    for _ in range(60):
        if child.poll() is not None:
            print(f'El proceso terminó. Consultar {log}; no se muestran secretos.')
            return False
        try:
            with urllib.request.urlopen(f'http://localhost:{port}/actuator/health', timeout=3) as response:
                if response.status == 200:
                    print(f'Backend {profile}: health UP.', flush=True)
                    return True
        except Exception:
            pass
        time.sleep(2)
    print('Tiempo de arranque agotado; consultar el log local.')
    return False

if __name__ == '__main__':
    args = sys.argv[1:]
    stopping = bool(args and args[0] == 'stop')
    if stopping:
        args = args[1:]
    profile = args[0] if args else 'prod'
    port = int(args[1]) if len(args) > 1 else (8080 if profile == 'prod' else 8082)
    sys.exit(0 if (stop(profile, port) if stopping else start(profile, port, args[2:])) else 1)
