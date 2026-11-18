---
machine: Hackback
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, gophish, log-poisoning, regeorg, winrm, named-pipe, diaghub, privesc]
---

# Hackback — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El puerto `80` sirve una instancia de GoPhish para campañas de phishing y varios vhosts que imitan marcas. Uno de ellos conduce a `admin.hackback.htb`, un panel con login ofuscado cuyo control en JavaScript se puede saltar. `webadmin.php` ofrece un gestor de archivos con directory walk, lectura y escritura, pero PHP y ASPX no se ejecutan. Se envenena el log de IIS con una webshell y se usa el gestor para moverse por el sistema de archivos; como no hay RCE, se sube `reGeorg` y se crea un túnel SOCKS hacia WinRM, donde las credenciales de un archivo de configuración dan shell como `simple`. Un named pipe mal configurado permite ejecutar como `hacker`. Para SYSTEM, el servicio `UserLogger` escribe un log en una ruta controlable, lo que permite colocar un DLL en `System32`; DiagHub lo carga con privilegios de SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,6666,64831 <IP>
```

- `80` Microsoft IIS 10.0.
- `6666` Microsoft HTTPAPI 2.0.
- `64831` TLS con un servicio no identificado.

```bash
ffuf -u http://<IP> -H "Host: FUZZ.hackback.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

El puerto `80` responde con la consola de GoPhish, que lista los dominios de las campañas de phishing.

## Enumeración

Los vhosts de phishing (`www.paypal.htb`, `www.facebook.htb`, entre otros) apuntan a la misma IP. Uno de los paneles lleva a `admin.hackback.htb`, cuyo login está protegido por una comprobación en JavaScript que se puede desactivar desde el navegador. La aplicación redirige a una ruta con un identificador largo:

```text
http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/
```

Un `gobuster` con extensión `.php` encuentra `webadmin.php`. El panel permite listar directorios, leer archivos y escribir archivos, pero las extensiones ejecutables están deshabilitadas.

## Foothold

Con lectura y escritura de archivos se envenena el log de IIS: se envía una petición cuyo `User-Agent` contiene código PHP y se incluye el log desde el gestor. Como PHP no se ejecuta, la vía útil es la lectura del sistema de archivos y la escritura de un túnel.

Se sube `reGeorg` (un `.aspx` o `.jsp` según el servidor) y se conecta un cliente SOCKS:

```bash
python3 reGeorgSocksProxy.py -p 1080 -u http://admin.hackback.htb/<RUTA>/tunnel.aspx
proxychains netexec winrm <IP> -u simple -p '<PASSWORD>'
```

Las credenciales salen de un archivo de configuración leído con el gestor. WinRM responde a través del túnel y devuelve una shell como `simple`.

## Movimiento lateral

La shell de `simple` está limitada por AppLocker y por el modo de lenguaje de PowerShell. La enumeración de named pipes descubre un pipe de un servicio que permite ejecutar comandos en el contexto de `hacker`. Una ruta alternativa es una inyección de comandos en `clean.ini`, que también lleva al mismo usuario.

```powershell
Get-ChildItem \\.\pipe\
```

Con la ejecución como `hacker` se obtiene acceso a más archivos y a la información necesaria para el siguiente salto.

## Escalada de privilegios

El servicio `UserLogger` se ejecuta como SYSTEM y escribe un log en una ruta cuya ACL permite redirigirlo. Se cambia el destino del log a un DLL colocado en `C:\Windows\System32`; después se invoca DiagHub (Microsoft Diagnostics Hub Standard Collector), que carga el DLL con privilegios de SYSTEM:

```powershell
reg query HKLM\System\CurrentControlSet\Services\userlogger
# redirigir el log y colocar el DLL
```

La ejecución del servicio de diagnóstico carga la biblioteca y devuelve una shell como SYSTEM.

## Evidencia

- Consola de GoPhish y vhosts de phishing.
- Bypass del login en JavaScript y acceso a `webadmin.php`.
- Log de IIS envenenado y lectura de archivos.
- `reGeorg` y túnel SOCKS hacia WinRM.
- Shell como `simple` y ejecución como `hacker` por named pipe.
- `UserLogger` con log redirigido y DLL cargado por DiagHub.

## Lecciones aprendidas

- Un panel de administración con lectura y escritura de archivos es peligroso aunque no ejecute código.
- El log poisoning sirve para leer y escribir, no solo para RCE.
- Un túnel HTTP puede convertir un servicio interno en accesible.
- AppLocker y el modo restringido de PowerShell no impiden enumerar y pivotar.
- Un servicio que escribe logs en una ruta controlable puede cargar código como SYSTEM.

## Mitigaciones y detección

- Retirar paneles de administración de producción y exigir MFA y allowlist de IP.
- Deshabilitar la escritura de archivos en el gestor web y validar rutas contra un directorio base.
- No registrar cabeceras de usuario sin sanear; separar logs de código.
- Restringir la creación de túneles y monitorizar conexiones SOCKS y WinRM internas.
- Revisar las ACL de los servicios que escriben logs y bloquear escrituras en `System32`.
- Alertar de la carga de DLL desde servicios de diagnóstico y de cambios en `ImagePath`.

## Referencias

- [0xdf — Hackback](https://0xdf.gitlab.io/2019/07/06/htb-hackback.html)
- [IppSec — Hackback](https://www.youtube.com/watch?v=B9nozi1PrhY)
- [Hack The Box — Hackback](https://app.hackthebox.com/machines/hackback)
