-- S14, paso 2. Solo para el esquema local de desarrollo.
-- Se puede repetir: completa hasta 5000 productos y 20000 ventas de carga.
-- Las ventas no tienen detalles y solo sirven para medir el listado.
-- El esquema actual usa ID_CATEGORIA. Las columnas de V4 se rellenan si existen.
whenever sqlerror exit sql.sqlcode rollback
set serveroutput on

declare
    v_cliente_id number;
    v_categoria_id number;
    v_ventas_existentes number;
    v_columna number;
begin
    if sys_context('USERENV', 'SESSION_USER') in ('SYS', 'SYSTEM') then
        raise_application_error(-20001, 'Usar un esquema de desarrollo, no SYS ni SYSTEM.');
    end if;
    select min(id) into v_categoria_id from categorias where estado = true;
    if v_categoria_id is null then
        raise_application_error(-20002, 'Se necesita una categoria activa para la carga.');
    end if;

    select min(id) into v_cliente_id
    from clientes where nombres = 'Carga S14' and apellidos = 'Pruebas';
    if v_cliente_id is null then
        insert into clientes (dni, nombres, apellidos, email, estado, fecha_creacion)
        values ('99991400', 'Carga S14', 'Pruebas', 'carga-s14@example.test', true, systimestamp)
        returning id into v_cliente_id;
    end if;

    insert into productos (nombre, precio, stock, estado, id_categoria, fecha_creacion)
    select s.nombre, round(dbms_random.value(1, 200), 2),
           trunc(dbms_random.value(0, 500)), true, v_categoria_id, systimestamp
    from (
        select 'Producto de prueba S14 ' || lpad(level, 5, '0') nombre
        from dual connect by level <= 5000
    ) s
    where not exists (select 1 from productos p where p.nombre = s.nombre);
    dbms_output.put_line('Productos insertados=' || sql%rowcount);

    select count(*) into v_ventas_existentes from ventas where cliente_id = v_cliente_id;
    insert into ventas (fecha, total, estado, cliente_id)
    select systimestamp - numtodsinterval(mod(level - 1, 365), 'DAY'),
           round(dbms_random.value(5, 500), 2), 'REGISTRADA', v_cliente_id
    from dual where level > v_ventas_existentes connect by level <= 20000;
    dbms_output.put_line('Ventas insertadas=' || sql%rowcount);

    select count(*) into v_columna from user_tab_columns
    where table_name = 'PRODUCTOS' and column_name = 'CREADO_POR';
    if v_columna = 1 then
        execute immediate 'update productos set creado_por = ''carga''
          where nombre like ''Producto de prueba S14 %'' and creado_por is null';
    end if;
    select count(*) into v_columna from user_tab_columns
    where table_name = 'VENTAS' and column_name = 'CREADO_POR';
    if v_columna = 1 then
        execute immediate 'update ventas set creado_por = ''carga''
          where cliente_id = :id and creado_por is null' using v_cliente_id;
    end if;
    dbms_output.put_line('Cliente de carga ID=' || v_cliente_id);
    commit;
exception
    when others then
        rollback;
        raise;
end;
/
select 'PRODUCTOS=' || count(*) from productos;
select 'VENTAS=' || count(*) from ventas;
