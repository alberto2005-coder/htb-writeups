---
machine: Reel2
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, owa, password-spray, responder, jea, powershell, sticky-notes]
---

# Reel2 — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una red social Wallstant en el 8080 permite recopilar nombres; con ellos se hace password spraying contra OWA. Tras entrar, se envía un enlace malicioso para capturar un hash NetNTLM con Responder y se crackea. La cuenta obtiene una sesión JEA restringida, de la que se escapa con funciones y el operador de llamada; las notas StickyNotes filtran credenciales de `jea_test_account` y su función `Check-File` lee la flag de root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443,8080,5985 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://<IP>:8080/FUZZ
```

## Enumeración

- IIS en 80/443, Wallstant en 8080 y WinRM en 5985.
- Wallstant permite registrar una cuenta y listar usuarios.
- OWA en 443 es el objetivo del spray.

## Acceso inicial

Se recogen nombres de la red social y se prueba una contraseña común contra OWA con SprayingToolkit. Con las credenciales válidas se inicia sesión y se envía un enlace a un recurso UNC propio; Responder captura el hash NetNTLMv2, que se crackea. Las credenciales permiten WinRM, pero la sesión queda limitada por JEA.

## Escalada de privilegios

La sesión JEA bloquea cmdlets, pero permite definir funciones y usar `&{ ... }`; con ese bypass se lanza una PowerShell en FullLanguage. En `Documents` están los archivos `.psrc`/`.pssc` de `jea_test_account` y StickyNotes guarda su contraseña. Se conecta con `-ConfigurationName jea_test_account` y se usa `Check-File C:\ProgramData\..\Users\Administrator\Desktop\root.txt`.

## Evidencia

- Spray válido y sesión en OWA.
- Hash NetNTLMv2 capturado y crackeado.
- Bypass de JEA y lectura de la flag con `Check-File`.

## Lecciones aprendidas

- La enumeración de usuarios alimenta el password spraying.
- Responder sigue siendo eficaz si se permiten salidas SMB.
- JEA mal configurado puede escaparse con funciones y call operators.

## Mitigación y detección

- Aplicar MFA y bloqueo tras intentos fallidos en OWA.
- Bloquear SMB saliente y exigir firma.
- Auditar roles JEA y no incluir funciones que lean rutas arbitrarias.

## Referencias

- [0xdf — Reel2](https://0xdf.gitlab.io/2021/03/13/htb-reel2.html)
- [IppSec — Reel2](https://www.youtube.com/watch?v=Ro2vXt_WFDQ)
- [Hack The Box — Reel2](https://app.hackthebox.com/machines/reel2)
