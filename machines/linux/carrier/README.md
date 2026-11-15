---
machine: Carrier
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, router, bgp, ftp, privesc]
---

# Carrier — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP expone la configuración del router `r1` y credenciales de administración. El panel de diagnóstico ejecuta comandos como root, lo que da control de `r1`. Desde ahí se anuncia por BGP una ruta hacia el servidor FTP, se captura el tráfico y se obtienen credenciales que permiten entrar al host y ser root.

## Reconocimiento

```bash
nmap -Pn -sU -sCV -p161 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` una aplicación de gestión de transportes.
- SNMP responde con una community válida y filtra procesos y configuración.
- `gobuster` encuentra `/diagnostics` y el panel de administración.

## Enumeración

- `snmpwalk` revela el usuario y la contraseña del panel de `r1`.
- `/diagnostics` permite ejecutar `ping` y `traceroute`; el parámetro no está saneado.
- La red interna usa BGP y el host tiene un servidor FTP con credenciales.

## Foothold

Se inyecta un comando en el diagnóstico y se obtiene una shell root en el router `r1`. Desde allí se modifica la configuración BGP para anunciar una ruta más específica hacia el servidor FTP.

```bash
curl -s -b 'PHPSESSID=<SESSION>' 'http://<IP>/diagnostics.php' --data-urlencode 'target=127.0.0.1; id'
```

## Movimiento lateral

`r1` anuncia la ruta y el tráfico FTP del host pasa por el router. Con `tcpdump` se capturan las credenciales en claro; se usan para entrar por SSH al servidor Linux.

```bash
tcpdump -i any -nn -A 'tcp port 21'
```

## Escalada de privilegios

La cuenta capturada tiene privilegios de root o permite reutilizar la contraseña de `root`; con `su` se obtiene la flag.

```bash
ssh <USER>@<IP>
su -
```

## Evidencia

- `snmpwalk` con credenciales del router.
- Inyección en `/diagnostics` y shell root en `r1`.
- Ruta BGP anunciada y captura FTP.
- Credenciales reutilizadas y root en el host.

## Lecciones aprendidas

- SNMP puede filtrar la configuración completa de un router.
- Un diagnóstico que pasa entrada a `system` es ejecución root.
- BGP sin autenticación permite desviar tráfico y capturar credenciales.

## Mitigación y detección

- Usar SNMPv3 y ACLs; no exponer la community.
- Validar los parámetros del diagnóstico y ejecutar sin privilegios.
- Firmar BGP (RPKI/BGPsec) y cifrar FTP con TLS.

## Referencias

- [0xdf — Carrier](https://0xdf.gitlab.io/2019/03/16/htb-carrier.html)
- [IppSec — Carrier](https://www.youtube.com/watch?v=2ZxRA8BgmnA)
- [Hack The Box — Carrier](https://app.hackthebox.com/machines/carrier)
