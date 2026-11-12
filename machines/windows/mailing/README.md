---
machine: Mailing
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, lfi, hmailserver, cve-2024-21413, monikerlink, ntlm, libreoffice]
---

# Mailing — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un LFI en el sitio lee la configuración de hMailServer y permite enviar correo como administrador. Con CVE-2024-21413 (MonikerLink) se filtra el hash NTLMv2 del administrador; al crackearlo se accede por WinRM. Un macro de LibreOffice completa la escalada.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p25,80,110,143,587,5985 <IP>
```

Se añade `mailing.htb` al hosts. La web tiene un visor de archivos y hMailServer gestiona el correo.

## Acceso inicial

El parámetro de descarga permite path traversal. Se lee la configuración de hMailServer:

```text
http://mailing.htb/download.php?file=..\..\..\Program Files (x86)\hMailServer\Bin\hMailServer.INI
```

La contraseña del panel se crackea con `john`/`hashcat`. Se accede a hMailServer y se crea un buzón.

## Movimiento lateral

Se envía un correo con un enlace `file://` manipulado (CVE-2024-21413) a un usuario. Al abrirlo, el cliente se conecta a un recurso UNC controlado y `Responder` captura el hash NTLMv2. Se crackea y se accede por WinRM:

```bash
evil-winrm -i <IP> -u <usuario> -p '<password>'
```

## Escalada a administrador

Se revisan aplicaciones instaladas y documentos del usuario. Se prepara un documento de LibreOffice con un macro que ejecuta una reverse shell; al abrirlo el usuario privilegiado, se obtiene una shell de administrador.

## Evidencia

- Path traversal y configuración redactada.
- Correo MonikerLink y captura NTLM.
- Hash crackeado redactado.
- Documento macro y shell admin.

## Lecciones aprendidas

- Un LFI puede exponer credenciales de servicios internos.
- MonikerLink afecta a clientes de correo sin parchear.
- NTLMv2 sigue siendo útil para movimiento lateral.
- Los macros de documentos siguen siendo un vector.

## Mitigación y detección

- Corregir el path traversal y validar rutas.
- Actualizar Outlook/Windows (CVE-2024-21413).
- Bloquear NTLM saliente y forzar Kerberos.
- Deshabilitar macros y aplicar ASR.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2024-21413>
- <https://www.hackthebox.com/machines/mailing>
- <https://www.hmailserver.com/>
