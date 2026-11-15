"""Mide el archivo final; no confunde tiempo de acciones con duración del video."""
import json,math,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
e=root/'docs/evidencias/s14-estabilizacion'
ffprobe=Path.home()/'AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffprobe.exe'
meta=json.loads(subprocess.check_output([str(ffprobe),'-v','error','-show_entries','format=duration,size','-of','json',str(e/'demo-respaldo.mp4')],text=True))['format']
r=json.loads((e/'video.json').read_text(encoding='utf-8'))
r.setdefault('segundosRecorrido',r['segundos'])
r.update(segundos=math.ceil(float(meta['duration'])),duracionVideoSegundos=float(meta['duration']),bytes=int(meta['size']),archivo='demo-respaldo.mp4',nota='Los marcadores de bloques se midieron durante las acciones; la duración final se midió con ffprobe.')
assert r['segundos']<=600
(e/'video.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('MP4 verificado:',r['duracionVideoSegundos'],'s;',r['bytes'],'bytes')
