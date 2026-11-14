---
machine: Mist
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, pluck, adcs, esc13, petitpotam, shadow-credentials]
---

# Mist — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Pluck CMS 4.7.18 permite leer `data/settings.php` y obtener la contraseña del administrador; se sube un módulo PHP malicioso y se obtiene `svc_web` en MS01. Un directorio compartido con enlaces permite ejecutar como `Brandon.Keywarp` y, tras PetitPotam y shadow credentials sobre `svc_cabackup`, se abusa de ESC13 para entrar en Certificate Managers y Backup Operators. Se copian las colmenas del DC y se extraen los hashes de Administrator.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,88,389,445 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u http://<DOMAIN>/FUZZ
```

## Enumeración

- MS01 ejecuta Apache/PHP con Pluck CMS 4.7.18.
- El parámetro de lectura permite acceder a `data/settings.php`.
- `C:\Common Applications` es escribible y se comparte por SMB.

## Acceso inicial

Se lee la configuración de Pluck y se crackea el hash del administrador. Con la sesión se sube un módulo ZIP con una webshell, que se ejecuta como `svc_web`. En MS01, se sobrescribe `Notepad.lnk` en el directorio compartido con un acceso a PowerShell; cuando `Brandon.Keywarp` lo abre, se obtiene su sesión.

## Escalada de privilegios

Con LDAP signing deshabilitado, PetitPotam obliga a MS01 a autenticarse y se retransmite a LDAP para obtener `svc_ca$`. Certipy añade una shadow credential a `svc_cabackup` y los templates ESC13 `ManagerAuthentication` y `BackupSvcAuthentication` conceden Certificate Managers y ServiceAccounts. Se usa `reg.py backup` para copiar SAM/SYSTEM/SECURITY, `secretsdump` extrae el hash de Administrator y se entra al DC.

## Evidencia

- Acceso a `settings.php` y webshell como `svc_web`.
- Enlace malicioso y shell de `Brandon.Keywarp`.
- Certificados ESC13, colmenas copiadas y shell de Administrator.

## Lecciones aprendidas

- Los CMS antiguos y los permisos de archivos comprometen todo el host.
- LDAP signing y channel binding son controles esenciales.
- ESC13 combina templates y grupos de forma difícil de ver sin auditar ADCS.

## Mitigación y detección

- Actualizar Pluck y restringir escritura en shares.
- Exigir LDAP signing, channel binding y EPA.
- Auditar templates con OID group links y limitar Enrollment Agents.

## Referencias

- [0xdf — Mist](https://0xdf.gitlab.io/2024/10/26/htb-mist.html)
- [IppSec — Mist](https://www.youtube.com/watch?v=5osU3Igzv_Y)
- [Hack The Box — Mist](https://app.hackthebox.com/machines/mist)
