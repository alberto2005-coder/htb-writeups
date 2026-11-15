---
machine: Intense
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, hash-length-extension, snmp, buffer-overflow, rop, privesc]
---

# Intense — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una SQLi en el login filtra el hash del admin; un ataque de extensión de hash forja la cookie y da acceso. Una API de logs con traversal lee credenciales SNMP de escritura, y `snmp-shell` da una shell. En localhost, `note_server` tiene un fallo de lógica y un buffer overflow con canario; un ROP con fuga de libc acaba en root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
nmap -Pn -sU -p161 <IP>
```

- `22` SSH, `80` nginx con una web de notas y `161/udp` SNMP.
- La aplicación permite registro, login y exportación de logs.
- El código fuente está disponible en la web.

## Enumeración

- El login es vulnerable a SQLi; se filtra el hash del admin, pero no se crackea.
- El código muestra que la sesión usa `sha1(secret + username)` y compara con el hash.
- Con `hash_extender` se añade un usuario admin y se firma la cookie.

```bash
hash_extender --data admin --secret <LEN> --append '&user=admin' --signature <HASH> --format sha1
```

## Foothold

La API de logs acepta una ruta y permite traversal. Se leen `/etc/snmp/snmpd.conf` y credenciales SNMP de escritura. Con `snmp-shell` se ejecuta una reverse shell.

```bash
snmp-shell -v 2c -c <COMMUNITY> <IP>
```

## Movimiento lateral

La shell es del usuario `snmp`. En localhost escucha `note_server` en 5001 y su código está en el home. El binario tiene un fallo de lógica: se puede escribir más allá del buffer y leer la canaria y la dirección de retorno.

## Escalada de privilegios

Se filtra la canaria y una dirección de libc con la primitiva de lectura; se construye un ROP con `dup2`, `execv` y `/bin/sh`, y se conecta al puerto 5001 mediante un túnel SSH. El proceso corre como root.

```bash
python3 pwn_note_server.py remote
```

## Evidencia

- SQLi y hash del admin.
- Extensión de hash y cookie forjada.
- Traversal de logs y credenciales SNMP.
- `snmp-shell` y usuario `snmp`.
- Buffer overflow, ROP y root.

## Lecciones aprendidas

- `sha1(secret + data)` es vulnerable a extensión de hash.
- Los logs y configuraciones exponen credenciales SNMP.
- SNMP con escritura permite ejecutar comandos.
- Un fallo de lógica puede convertir un overflow en fuga y ROP.

## Mitigación y detección

- Usar HMAC y comparaciones constantes para sesiones.
- Restringir la API de logs y normalizar rutas.
- Usar SNMPv3 y solo lectura.
- Compilar con canarios, ASLR y PIE; revisar binarios internos.

## Referencias

- [0xdf — Intense](https://0xdf.gitlab.io/2020/11/14/htb-intense.html)
- [IppSec — Intense](https://www.youtube.com/watch?v=nBg6zUalb7c)
- [Hack The Box — Intense](https://app.hackthebox.com/machines/intense)
