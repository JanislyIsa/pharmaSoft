"""Genera la colección reproducible S14. No contiene cuentas ni secretos."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = []
def caso(nombre, metodo, ruta, estado, datos=None, script='', auth=None):
    req = {'method': metodo, 'url': '{{baseUrl}}' + ruta,
           'header': [{'key': 'Accept', 'value': 'application/json'}]}
    if auth is not None: req['auth'] = auth
    if datos is not None:
        req['header'].append({'key': 'Content-Type', 'value': 'application/json'})
        req['body'] = {'mode': 'raw', 'raw': json.dumps(datos), 'options': {'raw': {'language': 'json'}}}
    code = f'pm.test("HTTP {estado}", () => pm.response.to.have.status({estado}));\n' + script
    items.append({'name': nombre, 'request': req, 'event': [{'listen': 'test', 'script': {'type': 'text/javascript', 'exec': code.splitlines()}}]})

noauth = {'type': 'noauth'}
caso('01 Login administrador', 'POST', '/auth/login', 200,
     {'username': 'admin', 'password': '{{adminPassword}}'}, 'pm.environment.set("tokenAdmin", pm.response.json().token);', noauth)
caso('02 Login vendedor', 'POST', '/auth/login', 200,
     {'username': 'vendedor', 'password': '{{vendedorPassword}}'}, 'pm.environment.set("tokenVendedor", pm.response.json().token);', noauth)
caso('03 Categoría de prueba', 'POST', '/categorias', 201,
     {'nombre': 'S14 Postman {{marca}}', 'descripcion': 'Datos sintéticos', 'estado': True}, 'pm.environment.set("categoriaId", pm.response.json().id);')
caso('04 Cliente nuevo', 'POST', '/clientes', 201,
     {'dni': '{{dni}}', 'nombres': 'Postman', 'apellidos': 'S14 {{marca}}', 'email': 's14-{{marca}}@example.test', 'estado': True}, 'pm.environment.set("clienteId", pm.response.json().id);')
caso('05 Producto stock tres', 'POST', '/productos', 201,
     {'nombre': 'S14 Postman {{marca}}', 'precio': 10, 'stock': 3, 'estado': True, 'categoriaId': '{{categoriaId}}'}, 'pm.environment.set("productoId", pm.response.json().id);')
caso('06 Página productos', 'GET', '/productos?pagina=0&tamanio=20', 200, script='pm.test("Paginación de servidor", () => { const p=pm.response.json(); pm.expect(p.contenido.length).to.be.at.most(20); pm.expect(p.totalElementos).to.be.above(5000); });')
caso('07 Venta válida', 'POST', '/ventas', 201,
     {'clienteId': '{{clienteId}}', 'detalles': [{'productoId': '{{productoId}}', 'cantidad': 1}]},
     'pm.environment.set("ventaId", pm.response.json().id); pm.environment.set("ventaRequestId", pm.response.headers.get("X-Request-Id")); pm.test("Total calculado por servidor", () => pm.expect(pm.response.json().total).to.eql(10));')
caso('08 Stock descontado', 'GET', '/productos/{{productoId}}', 200, script='pm.test("Stock 3 a 2", () => pm.expect(pm.response.json().stock).to.eql(2));')
caso('09 Auditoría venta', 'GET', '/auditoria?accion=VENTA_REGISTRADA&usuario=admin', 200, script='pm.test("Venta y correlación", () => pm.expect(pm.response.json().contenido.some(e => e.entidadId == pm.environment.get("ventaId") && e.requestId === pm.environment.get("ventaRequestId"))).to.eql(true));')
caso('10 Venta vacía', 'POST', '/ventas', 400, {'clienteId': '{{clienteId}}', 'detalles': []})
caso('11 Productos sin token', 'GET', '/productos', 401, auth=noauth)
caso('12 Auditoría vendedor', 'GET', '/auditoria', 403, auth={'type': 'bearer', 'bearer': [{'key': 'token', 'value': '{{tokenVendedor}}', 'type': 'string'}]})
caso('13 Producto inexistente', 'GET', '/productos/999999999', 404)
caso('14 Venta sin stock', 'POST', '/ventas', 409,
     {'clienteId': '{{clienteId}}', 'detalles': [{'productoId': '{{productoId}}', 'cantidad': 9999}]})
caso('15 Fallo conserva stock', 'GET', '/productos/{{productoId}}', 200, script='pm.test("409 no descuenta stock", () => pm.expect(pm.response.json().stock).to.eql(2));')
caso('16 Anular venta', 'PATCH', '/ventas/{{ventaId}}/anular', 200, script='pm.environment.set("anularRequestId", pm.response.headers.get("X-Request-Id")); pm.test("Estado anulado", () => pm.expect(pm.response.json().estado).to.eql("ANULADA"));')
caso('17 Auditoría anulación', 'GET', '/auditoria?accion=VENTA_ANULADA', 200, script='pm.test("Anulación confirmada", () => pm.expect(pm.response.json().contenido.some(e => e.entidadId == pm.environment.get("ventaId") && e.requestId === pm.environment.get("anularRequestId"))).to.eql(true));')
caso('18 Auditoría alta cliente', 'GET', '/auditoria?accion=CLIENTE_REGISTRADO', 200, script='pm.test("Alta sin datos personales", () => { const e=pm.response.json().contenido.find(e => e.entidadId == pm.environment.get("clienteId")); pm.expect(e).to.exist; pm.expect(e.detalle).not.to.include(pm.environment.get("dni")); pm.expect(e.detalle).not.to.include("@"); });')

collection = {'info': {'name': 'PharmaBackend S14 - regresión local', 'description': 'Ejecutar solo en la base local de demostración. Crea datos sintéticos nuevos. Variables secretas del entorno: adminPassword y vendedorPassword; no exportarlas ni guardar tokens. El 409 comprueba que el stock sigue en 2. La anulación cambia el estado según el contrato existente; no representa una devolución de inventario.', '_postman_id': 'fda902e0-4d1c-4536-b389-000000000014', 'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},
              'auth': {'type': 'bearer', 'bearer': [{'key': 'token', 'value': '{{tokenAdmin}}', 'type': 'string'}]},
              'variable': [{'key': 'baseUrl', 'value': 'http://localhost:8080/api/v1'}],
              'event': [{'listen': 'prerequest', 'script': {'type': 'text/javascript', 'exec': ['if (!pm.environment.get("marca")) { pm.environment.set("marca", Date.now()+"-"+Math.floor(Math.random()*100000)); pm.environment.set("dni", String(Math.floor(10000000+Math.random()*89999999))); }']}}], 'item': items}
out = ROOT / 'docs/postman/PharmaBackend.postman_collection.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Colección generada: {len(items)} solicitudes, sin secretos.')
