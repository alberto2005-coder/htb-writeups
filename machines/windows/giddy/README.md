---
machine: Giddy
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, sqli, winrm, ntlm, unifi-video, privilege-escalation]
---

# Giddy — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación IIS con SQLi permite extraer credenciales y entrar por WinRM. La enumeración local descubre el servicio UniFi Video ejecutado como SYSTEM con una versión vulnerable, lo que permite ejecutar comandos con privilegios altos.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,5985 <IP>
```

La web es una aplicación ASP.NET. Se enumeran rutas y parámetros con `feroxbuster`. El puerto 5985 (WinRM) está expuesto.

## Acceso inicial

El formulario de login es inyectable. Se usa `sqlmap` o una carga manual para extraer usuarios y hashes:

```bash
sqlmap -r login.txt --batch --dbs
```

Se crackean los hashes con `hashcat`/`john`. Las credenciales funcionan en WinRM:

```bash
evil-winrm -i <IP> -u <usuario> -p '<password>'
```

Si WinRM no acepta la contraseña directamente, se captura un hash NTLMv2 con `Responder` y se crackea.

## Enumeración local

```powershell
whoami /priv
Get-Service
Get-Process
```

Se identifica el servicio UniFi Video, que corre como SYSTEM y usa una versión antigua con una vulnerabilidad de ejecución de comandos.

## Escalada a SYSTEM

Se localiza el ejecutable y la versión del servicio. Se usa un exploit público para UniFi Video o se reemplaza un binario/script con permisos débiles. La ejecución se hace como SYSTEM:

```powershell
.\exploit.exe
whoami
```

Se lee la flag de administrator y se redacta.

## Evidencia

- Petición SQLi y volcado redactado.
- Sesión WinRM.
- Servicio UniFi Video y versión.
- `whoami` como SYSTEM.

## Lecciones aprendidas

- IIS y ASP.NET siguen exponiendo SQLi en formularios legacy.
- WinRM permite movimiento lateral con credenciales válidas.
- Los servicios de terceros como SYSTEM son objetivos de escalada.
- NTLMv2 sigue siendo útil cuando la contraseña no es reutilizable.

## Mitigación y detección

- Consultas parametrizadas y WAF.
- Restringir WinRM a administración.
- Actualizar UniFi Video y ejecutarlo con cuentas de servicio de bajo privilegio.
- Monitorizar creación de procesos desde servicios.

## Referencias

- <https://www.hackthebox.com/machines/giddy>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://github.com/swisskyrepo/PayloadsAllTheThings>
