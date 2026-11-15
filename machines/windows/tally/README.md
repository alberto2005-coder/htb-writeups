---
machine: Tally
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, sharepoint, ftp, keepass, mssql, seimpersonate]
---

# Tally — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SharePoint filtra credenciales de FTP. En el FTP hay una base KeePass y un instalador de Firefox; la base se crackea y da acceso SMB. Un binario en SMB contiene credenciales de MSSQL, y con `xp_cmdshell` se obtiene una shell con `SeImpersonate`. Una tarea programada que ejecuta un PowerShell escribible permite llegar a administrador.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,80,445,1433,3389,5985 <IP>
```

- Puertos: `21/tcp` FTP, `80/tcp` HTTP, `445/tcp` SMB, `1433/tcp` MSSQL, `3389/tcp` RDP y `5985/tcp` WinRM.
- Servicios: SharePoint, FTP, SMB, SQL Server y WinRM.
- Tecnologías: SharePoint, KeePass, MSSQL, PowerShell y SeImpersonate.

## Enumeración

- `tally.htb` con SharePoint.
- Credenciales FTP en páginas o listas accesibles.
- KeePass y Firefox en el FTP.
- Recurso SMB con un binario y MSSQL accesible.

## Foothold

Se extraen las credenciales FTP de SharePoint y se descarga el contenido. `keepass2john` y Hashcat recuperan la contraseña de la base; esa credencial abre SMB, donde un binario filtra el usuario y la contraseña de MSSQL.

```bash
curl -s http://tally.htb/
ftp tally.htb
keepass2john database.kdbx > keepass.hash
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt
netexec smb tally.htb -u <USER> -p '<PASS>' --shares
mssqlclient.py <DOMAIN>/<USER>:<PASS>@tally.htb -windows-auth
```

## Movimiento lateral

Con MSSQL se habilita `xp_cmdshell` y se ejecuta una shell como el usuario del servicio. Esa cuenta tiene `SeImpersonate`, que se explota con JuicyPotato o PrintSpoofer.

## Escalada de privilegios

La shell impersonada permite revisar tareas programadas. Una tarea ejecuta un script PowerShell escribible como administrador; se modifica para lanzar una shell y se espera a la siguiente ejecución.

```bash
whoami /priv
JuicyPotato.exe -l 1337 -p cmd.exe -a '/c whoami' -t *
schtasks /query /fo LIST /v
# Añadir la carga al script escribible de la tarea y esperar
schtasks /run /tn <TASK>
```

## Evidencia

- Credenciales FTP desde SharePoint.
- KeePass crackeado y acceso SMB/MSSQL.
- `SeImpersonate` y tarea programada modificada.

## Lecciones aprendidas

- SharePoint puede filtrar credenciales de otros servicios.
- Una base KeePass antigua es crackeable si la contraseña es débil.
- Las tareas programadas con scripts escribibles son una escalada clásica.

## Mitigación y detección

- Restringir SharePoint y rotar credenciales FTP.
- Usar KeePass con passphrase fuerte y KDF actualizado.
- Quitar `SeImpersonate` a cuentas de servicio y proteger scripts de tareas.

## Referencias

- [0xdf — Tally](https://0xdf.gitlab.io/2022/04/11/htb-tally.html)
- [IppSec — Tally](https://www.youtube.com/watch?v=l-wzBhc9wFc)
- [Hack The Box — Tally](https://app.hackthebox.com/machines/tally)
