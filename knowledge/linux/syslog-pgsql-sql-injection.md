---
topic: rsyslog a PostgreSQL — inyección SQL en plantillas
tags: [linux, rsyslog, postgresql, sqli, privesc]
---

# rsyslog a PostgreSQL — inyección SQL en plantillas

[🇬🇧 English](syslog-pgsql-sql-injection.en.md) | **Español**

## Concepto

El módulo `ompgsql` de rsyslog envía cada mensaje a PostgreSQL usando una plantilla. Si la plantilla concatena el mensaje sin parametrizar, el contenido de un log se convierte en SQL. Con `logger -p local7.info` cualquier usuario que pueda escribir en esa facility controla la consulta; las consultas apiladas y `COPY ... TO` permiten leer y escribir archivos como `postgres`.

## Cuándo aplica

- rsyslog reenvía logs a PostgreSQL con una plantilla `sql-syslog`.
- El usuario puede escribir en la facility configurada (`local7.info`).
- PostgreSQL acepta consultas apiladas y el usuario tiene permisos de archivo.

## Procedimiento

1. Leer `/etc/rsyslog.d/*.conf` y localizar la plantilla y la facility.
2. Enviar un mensaje con `'` y revisar `/var/log/postgresql`.
3. Cerrar la cadena con `', null)-- -` y probar `;`.
4. Usar `COPY ... TO` o `FROM PROGRAM` para ejecutar o escribir.

```bash
logger -p local7.info "test', null)-- -"
logger -p local7.info "x',null); CREATE TABLE aaa (c text);-- -"
```

```bash
logger -p local7.info "x',null); COPY (SELECT '') TO \\$$/tmp/pwned\\$$;-- -"
```

## Variantes

- `COPY ... FROM PROGRAM` para ejecución directa.
- Escribir `authorized_keys` de `postgres` con una tabla temporal.
- Leer `.psql_history` para obtener credenciales y reutilizarlas.

## Limitaciones

- rsyslog escapa `'` con `\`, hay que ajustar la sintaxis.
- El usuario de PostgreSQL puede no ser superusuario.
- `COPY ... PROGRAM` requiere permisos y una ruta escribible.

## Mitigación

- Parametrizar la plantilla o usar un formato JSON y una tabla staging.
- Restringir `pg_execute_server_program` y `COPY` a archivos.
- Separar la facility de logs de usuarios no confiables.

## Detección

- Errores de sintaxis SQL en logs de PostgreSQL.
- `COPY ... PROGRAM` o `COPY ... TO` en ` STATEMENT`.
- Mensajes de `logger` con comillas y comentarios SQL.

## Referencias

- [rsyslog — ompgsql](https://www.rsyslog.com/doc/configuration/modules/ompgsql.html)
- [0xdf — Zetta](https://0xdf.gitlab.io/2020/02/22/htb-zetta.html)
- [PostgreSQL — COPY](https://www.postgresql.org/docs/current/sql-copy.html)
