---
machine: Search
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, credentials, wdigest, bloodhound, gmsa, sebackup]
---

# Search — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web corporativa filtra credenciales en una imagen y permite entrar al dominio. La enumeración revela `WDigest` activo, una cuenta gMSA y privilegios de backup; con ellos se vuelca NTDS y se compromete el dominio.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p53,80,88,135,139,389,443,445,464,636,3268,5985 <IP>
```

Se añade `search.htb` al hosts. Se enumeran vhosts, usuarios y recursos SMB. Las imágenes del sitio pueden contener metadatos o texto con credenciales.

## Acceso inicial

Se descargan las imágenes y se revisan metadatos/OCR. Una credencial permite autenticarse en el dominio y acceder a SMB/WinRM.

```bash
smbclient -L //<IP> -U '<user>%<password>'
```

## Movimiento lateral

Se revisa el registro en busca de credenciales en claro:

```powershell
reg query HKLM\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\WDigest
```

Si `UseLogonCredential` está a 1, se puede extraer una credencial de memoria con `mimikatz`. Se ejecuta BloodHound y se identifican rutas hacia cuentas con más privilegios, incluida una gMSA.

## Escalada a administrador

Con `ReadGMSAPassword` o `SeBackupPrivilege` se obtiene material de credenciales. Se vuelca `NTDS.dit` y se extraen hashes:

```powershell
secretsdump.py -just-dc -ntds ntds.dit -system SYSTEM <user>@<IP>
```

Con el hash del administrador se accede al DC y se lee la flag.

## Evidencia

- Imagen con credencial redactada.
- `WDigest` y salida de BloodHound.
- gMSA/backup y volcado NTDS redactado.
- Acceso de administrador.

## Lecciones aprendidas

- Las imágenes y metadatos pueden filtrar credenciales.
- `WDigest` activo expone secretos en memoria.
- BloodHound revela rutas de privilegios ocultas.
- `SeBackupPrivilege` permite leer NTDS.

## Mitigación y detección

- Deshabilitar `WDigest` y proteger LSASS.
- Auditar gMSA y delegaciones.
- Restringir `SeBackupPrivilege`.
- Monitorizar acceso a `NTDS.dit` y tickets.

## Referencias

- <https://www.hackthebox.com/machines/search>
- <https://bloodhound.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1003/003/>
