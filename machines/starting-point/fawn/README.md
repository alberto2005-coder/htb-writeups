---
machine: Fawn
os: Linux
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/393
category: Starting Point
state: Retired
pwned: 2026-11-06
tags: [ftp, anonymous, misconfiguration]
---

# Fawn — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired · Starting Point · Linux · Very Easy

## TL;DR

El servicio **FTP (21/tcp)** permite el acceso **anónimo** y expone la flag en el directorio raíz del servidor. No hay explotación: solo un inicio de sesión sin credenciales.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

Resultado relevante:

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
```

- Único puerto expuesto: **21/tcp FTP** (`vsftpd 3.0.3`).
- No hay SSH ni servicios web, así que FTP es el objetivo principal.
- `vsftpd` suele permitir `anonymous` si no se ha endurecido la configuración.

## Enumeración

Comprobamos el acceso anónimo:

```bash
ftp <TARGET_IP>
# Name: anonymous
# Password: <Enter>
```

Si el servidor responde `230 Login successful`, el acceso anónimo está habilitado. Listamos el contenido:

```bash
ftp> ls -la
ftp> get flag.txt
ftp> bye
```

## Foothold

La flag está directamente en el directorio servido por FTP:

```bash
cat flag.txt
# <FLAG>
```

También se puede hacer de forma no interactiva:

```bash
wget -q ftp://anonymous:anonymous@<TARGET_IP>/flag.txt -O flag.txt
```

## Lecciones aprendidas

- El **FTP anónimo** es una de las primeras cosas que hay que comprobar cuando el puerto 21 está abierto.
- `vsftpd` puede exponer el sistema de archivos completo si no se aplica `chroot` y permisos mínimos.
- FTP transmite credenciales y datos en texto plano; en producción debería sustituirse por SFTP/FTPS.
- En Starting Point, el objetivo es interiorizar el flujo de enumeración, no buscar exploits.

## Mitigaciones y detección

**Cómo se corrige:**

- Deshabilitar el acceso anónimo (`anonymous_enable=NO`).
- Forzar **FTPS** (TLS) o migrar a **SFTP**.
- Aplicar `chroot_local_user=YES` y permisos mínimos.
- Limitar el acceso por IP y usar cuentas dedicadas con contraseñas robustas.

**Cómo se detectaría:**

- Alertas por logins `anonymous` en los logs de `vsftpd`.
- Monitorización de descargas de archivos sensibles desde el servidor FTP.
- Escaneos periódicos que detecten `Anonymous FTP login allowed`.

## Referencias

- [vsftpd documentation](https://security.appspot.com/vsftpd.html)
- [OWASP — FTP Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- MITRE ATT&CK: [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/), [T1021 Remote Services](https://attack.mitre.org/techniques/T1021/)
