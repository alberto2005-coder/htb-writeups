---
machine: Fuse
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, papercut, password-spray, rpc, winrm, seloaddriver, capcom]
---

# Fuse — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El panel de logs de PaperCut expone nombres de usuario y texto que permite construir una lista de contraseñas. Un spray SMB descubre una cuenta con contraseña por defecto y cambio obligatorio. Tras cambiarla, RPC revela credenciales de `svc-print`; esa cuenta tiene WinRM y `SeLoadDriverPrivilege`. Se carga el driver vulnerable Capcom.sys y se obtiene SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p53,80,88,135,139,389,445,636,3268,5985 <IP>
```

- Controlador de dominio `fabricorp.local`.
- IIS en 80, SMB, LDAP, Kerberos y WinRM.
- La web redirige a `fuse.fabricorp.local/papercut/logs/html/index.htm`.

## Enumeración

Se añaden el dominio y el host a `/etc/hosts` y se revisa el panel de PaperCut. Las páginas de trabajos de impresión muestran usuarios y nombres de documentos.

```bash
cewl http://fuse.fabricorp.local/papercut/logs/html/index.htm --with-numbers > words.txt
```

Con `crackmapexec` o `hydra` se prueba la lista contra SMB. Una cuenta, `bhult`, usa la contraseña por defecto `<DEFAULT_PASSWORD>` y exige cambiarla.

```bash
smbpasswd -r <IP> -U bhult
rpcclient -U 'bhult%<NEW_PASSWORD>' <IP>
```

## Foothold

`rpcclient` permite enumerar usuarios. El campo de descripción de `svc-print` contiene la contraseña `<SVC_PASSWORD>`. La cuenta tiene acceso WinRM.

```bash
crackmapexec winrm <IP> -u svc-print -p '<SVC_PASSWORD>'
evil-winrm -i <IP> -u svc-print -p '<SVC_PASSWORD>'
```

Se lee `user.txt`. La tarea programada `Revert Password and Expiry` devuelve la contraseña de `bhult` a su valor inicial cada minuto, por lo que el acceso RPC debe renovarse.

## Escalada de privilegios

```powershell
whoami /priv
```

`svc-print` tiene `SeLoadDriverPrivilege` habilitado. Se sube `Capcom.sys` y `EoPLoadDriver.exe`, se registra el driver y se ejecuta `ExploitCapcom.exe` para robar el token de SYSTEM.

```powershell
.\EoPLoadDriver.exe System\CurrentControlSet\dfserv C:\ProgramData\Capcom.sys
.\ExploitCapcom.exe
```

La herramienta lanza una shell como `NT AUTHORITY\SYSTEM`; se lee `root.txt`.

## Evidencia

- Panel de PaperCut con usuarios y documentos redactados.
- `smbpasswd` y `rpcclient queryuser` sin credenciales reales.
- `whoami /priv` mostrando `SeLoadDriverPrivilege`.
- `ExploitCapcom` y `whoami` como SYSTEM.

## Lecciones aprendidas

- Los paneles de impresión pueden filtrar usuarios y contexto para un spray.
- Una contraseña por defecto con cambio obligatorio no es segura si la política es débil.
- `SeLoadDriverPrivilege` permite cargar drivers vulnerables y escalar a kernel/SYSTEM.

## Mitigaciones y detección

- Restringir el acceso al panel de PaperCut y no publicar logs de trabajos.
- Forzar contraseñas únicas y eliminar las cuentas con credenciales por defecto.
- Retirar `SeLoadDriverPrivilege` a cuentas de servicio.
- Alertar de carga de drivers (Event ID 7045), creación de servicios y ejecución de `EoPLoadDriver` o `Capcom.sys`.

## Referencias

- <https://www.hackthebox.com/machines/Fuse>
- <https://attack.mitre.org/techniques/T1110/003/>
- <https://attack.mitre.org/techniques/T1068/>
- <https://learn.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-best-practices>
