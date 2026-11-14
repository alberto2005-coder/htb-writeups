---
machine: Minion
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, icmp, ssrf, powershell, ads]
---

# Minion — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio en 62696 tiene un `test.asp` que hace peticiones por el servidor y un panel `/backend` con ejecución de comandos. La única salida es ICMP, así que se construye una shell Python/PowerShell sobre pings. Una tarea programada ejecuta un script de PowerShell escribible; se secuestra para pasar a `decoder.MINION`. Un backup con un flujo alternativo guarda la contraseña de Administrator.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
62696/tcp http  Microsoft IIS 8.5
80/tcp    http  internal only
5985/tcp  winrm internal
```

## Enumeración

- `robots.txt` apunta a `/backend`, un panel ASP con ejecución.
- `test.asp?u=` hace peticiones desde el servidor (SSRF).
- El escaneo por SSRF encuentra 80, 5985 y 47001 en localhost.
- La salida a Internet solo permite ICMP.

## Foothold

Se sube un `cmd.aspx` desde el panel y se ejecuta `whoami`. Como no hay reverse shell TCP, se usa un script Python con Scapy que envía comandos en paquetes ICMP y recibe la salida del mismo modo; en el host, un bloque PowerShell ejecuta el comando y divide la respuesta.

```text
test.asp?u=http://127.0.0.1:80/
POST /cmd.aspx  xcmd=whoami
```

## Movimiento lateral

La enumeración por ICMP encuentra una tarea programada que ejecuta un script de PowerShell en una ruta escribible. Se reemplaza el script por uno que añade un usuario o ejecuta una shell, y la tarea lo lanza como `decoder.MINION`.

```powershell
schtasks /query /fo LIST /v
```

## Escalada de privilegios

Un backup ZIP contiene un flujo alternativo NTFS con la contraseña de Administrator. Se lee con `Get-Content -Stream` o desde Linux con `ntfs-3g`/`7z`. Con esas credenciales se abre WinRM o `runas` y se obtiene Administrator.

```powershell
Get-Item .\backup.zip -Stream *
Get-Content .\backup.zip -Stream <STREAM>
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un SSRF permite alcanzar servicios ligados a localhost.
- ICMP puede ser un canal C2 completo si es la única salida.
- Las tareas programadas con scripts escribibles son un secuestro clásico.
- Los flujos alternativos NTFS ocultan datos a una enumeración básica.

## Mitigaciones y detección

- Eliminar `test.asp` y restringir el panel `/backend`.
- Filtrar la salida y no permitir ICMP arbitrario.
- Proteger scripts de tareas programadas y revisar sus ACL.
- Analizar flujos alternativos y no guardar contraseñas en backups.

## Referencias

- [0xdf — Minion](https://0xdf.gitlab.io/2022/04/07/htb-minion.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+minion)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+minion+writeup)
