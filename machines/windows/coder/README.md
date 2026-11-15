---
machine: Coder
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, smb, dotnet, keepass, teamcity, adcs, certifried]
---

# Coder — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un share SMB contiene un ejecutable .NET y un archivo cifrado. La ingeniería inversa revela el fallo de cifrado y permite recuperar una base KeePass y su keyfile, con credenciales de TeamCity y un backup 2FA. El plugin de Chrome se invierte para recuperar el seed TOTP, el pipeline CI/CD da shell y un diff filtra credenciales de `e.black`. Con PKI Admins se crea una plantilla sin extensión de seguridad y se explota Certifried (CVE-2022-26923) para obtener el DC y Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,139,389,445,5985,9389 <IP>
```

- El host es un controlador de dominio de `coder.htb`.
- SMB, LDAP, Kerberos y WinRM están abiertos.
- `netexec smb <IP> -u guest -p '' --shares` muestra un share de desarrollo.

## Enumeración

- El share contiene `Coder.exe`, `Coder.enc` y notas de compilación.
- `dotPeek` muestra el algoritmo de cifrado y una clave derivada de un valor fijo.
- Al descifrar `Coder.enc` se obtienen una base KeePass y un keyfile.

```bash
smbclient //<IP>/Development -N
dotpeek Coder.exe
kpcli --kdb coder.kdbx --key coder.key
```

## Foothold

La base contiene credenciales de `svc_teamcity` y un backup 2FA. El plugin de Chrome que genera el backup se puede invertir: el seed TOTP está cifrado con una contraseña débil, que se crackea. Con el código de 6 dígitos se entra en TeamCity.

```bash
hashcat -m 16500 backup.hash rockyou.txt
```

## Movimiento lateral

Como usuario con permisos de build se crea una rama con un diff que ejecuta comandos en el pipeline. El agente corre como `svc_teamcity` y permite leer `C:\ProgramData\JetBrains\TeamCity\system\changes`. Un diff antiguo contiene `Get-ADCS_Report.ps1`, `key.key` y `enc.txt`; el script descifra la contraseña de `e.black`.

```powershell
Get-ChildItem C:\ProgramData\JetBrains\TeamCity\system\changes
```

## Escalada de privilegios

`e.black` está en `PKI Admins` y puede importar plantillas de AD CS. Se crea una plantilla con `CT_FLAG_NO_SECURITY_EXTENSION` y, como `s.blade`, se añade un equipo al OU `BuildAgents` con `dNSHostName` igual al del DC. Se matricula el equipo con la plantilla, se obtiene un certificado como DC y se hace `secretsdump`. Con el hash de Administrator se entra por WinRM.

```bash
certipy-ad template -u e.black@coder.htb -p '<PASSWORD>' -dc-ip <DC> -template ESC1 -no-security-extension
certipy-ad req -u 'DC01$'@coder.htb -p '<MACHINE_PASSWORD>' -ca coder-DC01-CA -template ESC1 -dc-ip <DC>
certipy-ad auth -pfx dc01.pfx -dc-ip <DC>
```

## Evidencia

- Share SMB con binario .NET y archivo cifrado.
- KeePass con keyfile y credenciales de TeamCity.
- Backup 2FA y seed TOTP recuperado.
- Pipeline CI/CD y diff con credenciales de `e.black`.
- Plantilla AD CS y Certifried hasta Administrator.

## Lecciones aprendidas

- La ingeniería inversa de un binario de cifrado puede revelar la clave.
- Un backup 2FA sin protección fuerte equivale a perder el segundo factor.
- Los pipelines CI/CD son ejecución remota y sus artefactos filtran secretos.
- Certifried sigue vivo si una plantilla omite la extensión de seguridad.

## Mitigación y detección

- No almacenar secretos en shares de desarrollo ni en artefactos de build.
- Proteger los backups TOTP con contraseñas fuertes y almacenamiento aislado.
- Auditar plantillas AD CS y bloquear `CT_FLAG_NO_SECURITY_EXTENSION`.
- Revisar la creación de equipos con `dNSHostName` de DC y los cambios en `PKI Admins`.

## Referencias

- [0xdf — Coder](https://0xdf.gitlab.io/2023/12/16/htb-coder.html)
- [IppSec — Coder](https://www.youtube.com/watch?v=uZiEKiG96VI)
- [Hack The Box — Coder](https://app.hackthebox.com/machines/coder)
