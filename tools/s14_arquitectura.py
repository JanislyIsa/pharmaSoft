"""Diagrama exportable de componentes y despliegue local."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1600,950),'#f4f7fb');d=ImageDraw.Draw(im)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',31)
normal=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
d.text((70,40),'PharmaSoft: componentes y despliegue local',font=bold,fill='#12315d')
d.text((70,91),'Navegador -> Nginx / Angular -> Spring Boot -> Oracle y Redis',font=normal,fill='#426080')
def caja(x,y,w,h,title,lines):
    d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill='white',outline='#b8c7dd',width=2)
    d.rounded_rectangle((x,y,x+w,y+60),radius=18,fill='#12315d')
    d.rectangle((x,y+32,x+w,y+60),fill='#12315d')
    d.text((x+18,y+15),title,font=bold,fill='white')
    for i,t in enumerate(lines):d.text((x+18,y+83+i*38),t,font=small,fill='#173657')
def flecha(a,b,label,x,y):
    d.line((*a,*b),fill='#e4a600',width=6)
    import math
    angle=math.atan2(b[1]-a[1],b[0]-a[0]);p=b
    d.polygon([p,(p[0]-18*math.cos(angle-.5),p[1]-18*math.sin(angle-.5)),(p[0]-18*math.cos(angle+.5),p[1]-18*math.sin(angle+.5))],fill='#e4a600')
    d.text((x,y),label,font=small,fill='#173657')
caja(60,190,400,215,'Navegador / Angular 22',['Vendedor, almacén y admin','Rutas diferidas + guards','JWT en sessionStorage'])
caja(590,190,410,215,'Nginx - Docker :8081',['SPA compilada + gzip','Fallback de rutas Angular','/api y /actuator -> backend'])
caja(590,515,410,300,'Spring Boot 4 / Java 21',['Host Windows :8080 (dev)','Security -> controlador','Servicio @Transactional','JPA + eventos AFTER_COMMIT','Actuator y requestId/MDC'])
caja(1140,500,400,190,'Oracle - Docker :1522',['FREEPDB1 / JPA / Flyway','Ventas, stock y bitácora'])
caja(1140,740,400,160,'Redis - Docker :6379',['Catálogos; TTL 10 minutos','Se invalida al escribir'])
flecha((460,275),(590,275),'HTTP',490,225)
flecha((795,405),(795,515),'REST + Bearer',815,442)
flecha((1000,590),(1140,590),'JDBC',1030,540)
flecha((1000,770),(1140,820),'Caché',1020,785)
d.text((60,535),'Desarrollo alternativo',font=bold,fill='#12315d')
d.text((60,590),'ng serve :4200 -> API :8080',font=small,fill='#173657')
d.text((60,640),'Pruebas: Playwright + Postman',font=small,fill='#173657')
d.text((60,695),'Oracle es la fuente de verdad.',font=small,fill='#173657')
d.text((60,730),'Redis no reemplaza la base.',font=small,fill='#173657')
d.text((60,875),'Configuración real: deploy/docker-compose.yml, nginx.conf y application-*.yaml.',font=small,fill='#426080')
im.save(root/'docs/arquitectura.png')
print('Diagrama creado 1600 x 950.')
