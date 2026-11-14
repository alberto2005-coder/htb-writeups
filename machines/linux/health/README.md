---
machine: Health
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, laravel, ssrf, gogs, sqlite, sqli, cron]
---

# Health — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación Laravel redirige a una URL de monitorización y permite SSRF. El servicio interno Gogs filtra la tabla de usuarios mediante una SQLi en SQLite; el hash crackeado da SSH. Un cron que consulta la base de datos ejecuta tareas y permite escribir un comando como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,3000 <IP>
```

- SSH, HTTP y un servicio interno.
- La web es una plataforma de salud con formularios y redirecciones.
- Hay un Gogs accesible desde localhost.

## Enumeración

- Una ruta de monitorización acepta una URL y devuelve una redirección.
- El parámetro permite solicitar `http://127.0.0.1:3000` y alcanzar Gogs.
- La versión de Gogs tiene una SQLi en el buscador de usuarios.
- La base SQLite contiene usuarios y hashes.

## Foothold

Se usa la redirección/SSRF para consultar Gogs. La SQLi se explota con una unión y se extrae el hash de un usuario. Se crackea fuera de la plataforma y se accede por SSH.

```bash
curl -s 'http://health.htb/monitor' --data-urlencode 'url=http://127.0.0.1:3000'
sqlmap -r gogs.req --dbms=sqlite
```

## Escalada de privilegios

Un cron ejecuta una tarea que lee de la base de datos y pasa el resultado a un comando. Se inserta una tarea con un payload controlado; al ejecutarse como root, se obtiene una shell o se copia un binario con SUID.

```bash
pspy64
sqlite3 <DB> '.tables'
```

## Evidencia

- SSRF contra Gogs.
- Hash extraído y sesión SSH.
- Tabla de tareas y ejecución del cron.
- Root mediante la tarea inyectada.

## Lecciones aprendidas

- Las redirecciones internas pueden saltarse el filtrado de SSRF.
- Un Gogs antiguo añade una SQLi a la cadena.
- Los cron que consumen datos de usuario son una vía de escalada.
- La base SQLite es un objetivo de lectura y escritura.

## Mitigaciones y detección

- Validar destinos y no seguir redirecciones internas.
- Actualizar Gogs y usar consultas parametrizadas.
- No ejecutar tareas de usuario con privilegios de root.
- Alertar de consultas a bases desde cron y cambios en tareas.
- Referencias: CVE-2022-30781, OWASP SSRF, HTB Health.

## Referencias

- <https://www.hackthebox.com/machines/Health>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-30781>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1053/003/>
