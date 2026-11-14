---
machine: Axlle
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, xll, phishing, url-file, bloodhound, lolbin]
---

# Axlle — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un controlador de dominio con web corporativa, SMTP, RDP y WinRM. Se envía un archivo XLL de Excel malicioso a `gideon.hamill` y se obtiene una shell; un archivo `.url` en un directorio compartido entrega la sesión a `dallon.matrix`. El historial de PowerShell filtra credenciales, BloodHound guía hasta `baz.humphries` y el LOLBIN `StandaloneRunner.exe` permite llegar a Administrator.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p25,80,88,389,445,3389,5985 <IP>
bloodhound-python -u <USER> -p <PASS> -d <DOMAIN> -ns <IP> -c All
```

## Enumeración

- Puertos de AD DS, SMTP (25), HTTP (80), RDP y WinRM.
- SMB rechaza acceso nulo e invitado.
- La web lista empleados y correos; hay un directorio compartido escribible.

## Acceso inicial

Se compila un XLL de Excel con una reverse shell y se envía por SMTP a `gideon.hamill`; al abrirlo se obtiene su sesión. En su host se crea un archivo `.url` en una ruta compartida que `dallon.matrix` abre, lo que entrega una segunda shell. El historial de PowerShell de `dallon.matrix` contiene credenciales en texto claro.

## Escalada de privilegios

Con esas credenciales se recoge BloodHound y se identifica la ruta sobre `baz.humphries`/`jacob.greeny`; se cambia la contraseña de la cuenta comprometida y se entra por WinRM. Desde ahí se abusa de `StandaloneRunner.exe`, un LOLBIN firmado, para ejecutar una shell con privilegios de Administrator.

## Evidencia

- Correo con el XLL y conexión de `gideon.hamill`.
- Archivo `.url` y shell de `dallon.matrix`.
- BloodHound, WinRM y ejecución mediante `StandaloneRunner.exe`.

## Lecciones aprendidas

- Los add-ins de Office siguen siendo un vector de phishing eficaz.
- Los archivos `.url` y `.lnk` en shares escribibles permiten ejecución al abrirlos.
- Los LOLBIN firmados dificultan la detección y deben auditarse.

## Mitigación y detección

- Bloquear XLL no confiables y aplicar Mark-of-the-Web.
- Restringir la escritura en shares y revisar accesos a `.url`/`.lnk`.
- Aplicar WDAC/AppLocker y monitorizar `StandaloneRunner.exe`.

## Referencias

- [0xdf — Axlle](https://0xdf.gitlab.io/2024/11/16/htb-axlle.html)
- [IppSec — Axlle](https://www.youtube.com/watch?v=cAXptAMDXuY)
- [Hack The Box — Axlle](https://app.hackthebox.com/machines/axlle)
