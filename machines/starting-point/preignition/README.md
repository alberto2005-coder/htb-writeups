---
machine: Preignition
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, web, gobuster, default-credentials]
---

# Preignition — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available (Starting Point), publicable.
> Ficha de referencia. Sin flags ni credenciales reales.

## TL;DR

Un nginx con una página "en construcción" y un **panel de administración** que no está enlazado desde ningún sitio. El descubrimiento de directorios da con `/admin.php`, y el panel usa **`admin:admin`**. Dentro está la flag. No hay ejecución de comandos ni escalada: es pura enumeración web y credenciales por defecto.

## Reconocimiento

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH
80/tcp  http  nginx 1.14.2
```

La portada solo muestra una plantilla con "website is under construction".

## Enumeración

```bash
gobuster dir -u http://<IP>/ -w /usr/share/seclists/Discovery/Web-Content/common.txt -x php
```

```text
/admin.php            (Status: 200)
```

También se llega con `feroxbuster -u http://<IP> -x php` o mirando `robots.txt`, que a veces anuncia el panel.

## Foothold

```text
http://<IP>/admin.php
usuario:  admin
password: admin
```

Tras el login, la propia página muestra la flag:

```text
<flag>
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

```text
/admin.php  ->  <flag>
```

## Lecciones aprendidas

- Un panel oculto no es un panel protegido: el descubrimiento de contenido lo encuentra en segundos.
- Las credenciales por defecto (`admin:admin`) siguen siendo la causa número uno de accesos en aplicaciones de ejemplo.
- Mitigación: retirar paneles de ejemplo en producción, contraseñas fuertes con MFA, rate limiting y bloqueo por intentos.
- Detección: picos de 404 por usuario y logins correctos desde IPs nuevas.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [rop-stack](../../../knowledge/pwn/rop-stack.md)
