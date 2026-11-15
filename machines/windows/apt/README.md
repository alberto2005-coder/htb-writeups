---
machine: APT
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ad, ipv6, ntlm, kerberos, dcsync]
---

# APT — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Solo RPC y HTTP responden en IPv4, pero RPC filtra una dirección IPv6 que expone todos los puertos del DC. Un backup SMB anónimo contiene `ntds.dit` y el registro SYSTEM; tras romper el ZIP se vuelcan 2.000 hashes. La reutilización de un hash da acceso al registro, de ahí a `henry.vinson_adm` y a WinRM. Con NTLMv1 habilitado, la coerción y el relay permiten obtener derechos de DCSync.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,135 <IP>
```

- `80/tcp` IIS 10 con una web de hosting y `135/tcp` MSRPC; el resto de puertos parece filtrado.
- RPC responde a `IOXIDResolver` y devuelve una dirección IPv6 del DC.
- Al escanear esa IPv6 aparecen `53`, `88`, `389`, `445`, `5985` y el resto de servicios de Active Directory.

## Enumeración

- El share `backup` permite acceso anónimo y contiene `backup.zip` con `Active Directory/ntds.dit` y `registry/SYSTEM`.
- `zip2john` y `hashcat -m 17220` recuperan la contraseña del ZIP.
- `secretsdump.py -system ... -ntds ... LOCAL` extrae unos 2.000 hashes; `kerbrute` confirma `henry.vinson` como usuario válido.

## Foothold

El hash de `henry.vinson` no funciona directamente, así que se prueban todos los hashes del volcado con `pyKerbrute` hasta encontrar el que corresponde a la cuenta. Con ese hash se consulta el registro remoto y se leen las credenciales de `henry.vinson_adm` en `HKU\SOFTWARE\GiganticHostingManagementSystem`, que sí tiene acceso a WinRM.

```bash
secretsdump.py -system registry/SYSTEM -ntds 'Active Directory/ntds.dit' LOCAL > ad_dump
cat ad_dump | grep ':::' | cut -d: -f3-4 > hashes
python3 pyKerbrute.py -domain htb.local -users henry.vinson -passwords hashes -dc-ip <IP>
reg.py -hashes :<HASH> htb.local/henry.vinson@htb.local query -keyName 'HKU\SOFTWARE\GiganticHostingManagementSystem'
evil-winrm -i <IP> -u henry.vinson_adm -p '<PASSWORD>'
```

## Movimiento lateral

El historial de PowerShell de `henry.vinson_adm` revela que se activó `lmcompatibilitylevel=2`, lo que permite NTLMv1. Se usa RoguePotato para forzar la autenticación de una cuenta privilegiada y un servidor RPC modificado con `ntlmrelayx` para retransmitirla a LDAP, donde se conceden derechos de DCSync.

## Escalada de privilegios

Con el relay completado se ejecuta `secretsdump.py` contra el DC para volcar todos los hashes del dominio, incluido el de `administrator`, y se obtiene acceso total.

```bash
ntlmrelayx.py -t ldap://<DC> -smb2support --escalate-user henry.vinson_adm
secretsdump.py -just-dc htb.local/administrator@<DC>
```

## Evidencia

- IPv6 del DC obtenida por RPC.
- `backup.zip` descargado y hashes volcados.
- Acceso WinRM como `henry.vinson_adm` y DCSync completado.

## Lecciones aprendidas

- Los servicios IPv6 pueden exponer puertos que IPv4 filtra.
- Un backup de AD accesible por SMB equivale a comprometer todas las cuentas.
- NTLMv1 y la coerción de autenticación siguen siendo una cadena viable.

## Mitigación y detección

- Restringir IPv6 y RPC a la red administrativa.
- Cifrar y limitar los backups de AD; no exponer `ntds.dit` por SMB anónimo.
- Deshabilitar NTLMv1, exigir signing y monitorizar relays LDAP.

## Referencias

- [0xdf — APT](https://0xdf.gitlab.io/2021/04/10/htb-apt.html)
- [IppSec — APT](https://www.youtube.com/watch?v=eRnqtXwCZVs)
- [Hack The Box — APT](https://app.hackthebox.com/machines/apt)
