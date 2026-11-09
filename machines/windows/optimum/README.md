---
machine: Optimum
os: Windows
difficulty: Easy
platform: Hack The Box
category: Web / Windows
state: Retired
tags: [rejetto, hfs, cve-2014-6287, ms16-032, windows]
---

# Optimum — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Sólo hay un puerto: **80** con `HttpFileServer 2.3` (Rejetto HFS). La macro `%00` de búsqueda (CVE-2014-6287) ejecuta comandos como `kostas`; para llegar a **SYSTEM** se usa **MS16-032** (handle del *Secondary Logon*), o cualquier bypass de UAC conocido de la época.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp open  http   HttpFileServer httpd 2.3
```

La página se identifica como `HFS 2.3` en la cabecera y en el título.

## Acceso

**CVE-2014-6287** — el parámetro de búsqueda (`search=%00{.exec|...}`) acaba en una llamada a `find` sin sanear:

```text
GET /?search=%00{.exec|cmd.exe /c powershell -nop -w hidden -c "..." .}
```

Módulo de MSF: `exploit/windows/http/rejetto_hfs_exec` → sesión como `kostas`.

## Escalada

`kostas` es usuario normal: comprobar parches y privilegios.

```text
systeminfo
whoami /priv
```

**MS16-032** (CVE-2016-0099) escala desde un proceso con varios handles en el *Secondary Logon*; el exploit público compila con PowerShell y lanza un cmd como `NT AUTHORITY\SYSTEM`. Alternativas de la misma época: Watson, `JuicyPotato` si hay `SeImpersonate`.

## Tropiezos

- **Payload de 32/64 bits**: la caja es de 2016; un binario x64 en un SO x86 no arranca.
- **Ejecución ciega**: sin salida en la respuesta, conviene una reverse shell.
- **Defender**: puede borrar el ejecutable del exploit; usar rutas en `C:\Windows\Temp` y compilar en memoria.

## Lecciones

- Un servidor de ficheros de usuario final en el puerto 80 es superficie web, con CVEs de RCE.
- En Windows antiguo, la escalada suele ser **falta de parches**, no mala configuración.
- `systeminfo` + `whoami /priv` deciden la ruta en un minuto.
