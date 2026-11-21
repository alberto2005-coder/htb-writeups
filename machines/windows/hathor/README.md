---
machine: Hathor
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, mojoportal, applocker, dll, certificate, dcsync, kerberos, privesc]
---

# Hathor — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

mojoPortal acepta las credenciales por defecto `admin@admin.com` / `<PASSWORD>`; se sube una webshell y se copia a `.aspx` para obtener shell como `web`. Desde `web` se leen los CSV de `Get-bADpasswords` y se obtiene el hash de `BeatriceMill`; como NTLM está deshabilitado, se usa Kerberos (`kinit`) para acceder por SMB. El share permite sobrescribir `7-zip64.dll`, que carga la tarea de `Bginfo64.exe` y da shell como `GinaWild`; con esa cuenta se toma posesión de `Bginfo64.exe` y se reemplaza para obtener otra shell. Un certificado de firma en la papelera permite modificar y firmar `Get-bADpasswords.ps1`, que se ejecuta como `bpassrunner`; con sus permisos de replicación se hace DCSync y, con el hash de Administrator, se obtiene un ticket Kerberos y una shell elevada.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985 <IP>
```

- `53`, `88`, `389`, `636`, `3268` y `3269`: DNS, Kerberos y LDAP de un controlador de dominio.
- `80`: IIS con mojoPortal.
- `445`: SMB, clave para la cadena de DLL y para los shares.
- `5985`: WinRM.

```bash
echo '<IP> hathor.windcorp.htb' | sudo tee -a /etc/hosts
```

## Enumeración

El sitio es mojoPortal. Las credenciales por defecto del portal permiten entrar como administrador. Desde el panel se sube un archivo y se descubre que la extensión se valida de forma débil: se sube una webshell con una extensión permitida y se copia a `.aspx` para que IIS la ejecute.

La ejecución está limitada por AppLocker y el firewall de Windows. La enumeración de procesos, shares y políticas muestra qué binarios y DLL están permitidos y qué share usa una tarea programada.

## Foothold

mojoPortal permite subir una webshell con una extensión permitida y copiarla a `.aspx`; el resultado es una shell como `web`. En el share `share` aparecen `AutoIt3_x64.exe`, `Bginfo64.exe`, la librería `7-zip64.dll` y scripts. Una tarea ejecuta `Bginfo64.exe` cada pocos minutos y carga la DLL desde una ruta escribible; AppLocker permite ambos binarios. Desde `web` también se puede leer `C:\Get-bADpasswords\Accessible\CSVs`. La explotación del share se hace en el movimiento lateral, cuando se obtiene acceso SMB.

```text
\\<HOST>\share\7-zip64.dll  → carga en el proceso programado
\\<HOST>\share\Bginfo64.exe → ejecución aprobada por AppLocker
```

## Movimiento lateral

`web` lee los CSV de `C:\Get-bADpasswords\Accessible\CSVs` y obtiene el hash de `BeatriceMill`; se crackea. Como NTLM está deshabilitado, `kinit beatricemill` pide un ticket Kerberos y `smbclient -k` accede al share `share`. Allí se sobrescribe `7-zip64.dll`; cuando la tarea ejecuta `Bginfo64.exe`, la DLL corre como `GinaWild` y devuelve una shell. `GinaWild` está en `ITDep` y puede tomar posesión de `Bginfo64.exe`; se reemplaza con `nc64.exe` y la tarea lanza una segunda shell como `GinaWild`.

En el escritorio público hay un acceso directo a `bAD Passwords.lnk`, que apunta a `C:\Get-bADpasswords\run.vbs`; el script crea un evento y se ejecuta con una cuenta privilegiada. En la papelera de reciclaje de `GinaWild` hay certificados `.pfx`; uno de ellos sirve para firmar código. Con el certificado se modifica el script de `Get-bADpasswords` y se firma, de modo que al ejecutarse como `bpassrunner` lanza una acción controlada.

## Escalada de privilegios

Como `bpassrunner` se tiene acceso a la información que el script recopila y a permisos de replicación. Se ejecuta `Get-ADReplAccount` contra el controlador para obtener el hash de Administrator. Como NTLM está deshabilitado, el hash no se usa directamente: se pide un TGT con `getTGT.py` y se usa la cache Kerberos para la shell elevada.

```powershell
Get-ADReplAccount -SamAccountName administrator -Server 'hathor.windcorp.htb'
```

```bash
getTGT.py -hashes :<NTHASH> windcorp.htb/administrator
KRB5CCNAME=./administrator.ccache evil-winrm -i hathor.windcorp.htb -r WINDCORP.HTB
```

## Evidencia

- Login en mojoPortal con las credenciales por defecto.
- Webshell copiada a `.aspx` y ejecución pese a AppLocker.
- DLL y EXE sobrescritos en el share y shell como `GinaWild`.
- Hash de `BeatriceMill` crackeado y acceso SMB con Kerberos.
- Certificado `.pfx` recuperado de la papelera y script firmado.
- Ejecución como `bpassrunner` y DCSync.
- Ticket Kerberos y shell como Administrator.

## Lecciones aprendidas

- Cambiar las credenciales por defecto de los portales no es opcional.
- AppLocker y el firewall reducen el impacto, pero no impiden abusar de binarios y DLL permitidos.
- Un share escribible con tareas programadas es ejecución de código.
- Los certificados de firma de código en la papelera permiten firmar payloads como si fueran legítimos.
- DCSync funciona aunque NTLM esté deshabilitado; Kerberos es la alternativa.

## Mitigaciones y detección

- Cambiar credenciales por defecto y aplicar MFA en portales de administración.
- Restringir la subida de archivos y validar extensión y contenido en el servidor.
- Aplicar AppLocker/WDAC con reglas por ruta y firma, y revisar las excepciones.
- No dar escritura a usuarios en shares con DLL o EXE ejecutados por tareas.
- Proteger los certificados de firma y revocar los que acaben en la papelera.
- Monitorizar DCSync, `Get-bADpasswords`, creación de tickets y ejecución de scripts firmados.

## Referencias

- [0xdf — Hathor](https://0xdf.gitlab.io/2022/11/19/htb-hathor.html)
- [IppSec — Hathor](https://www.youtube.com/watch?v=yweDaXZdt4s)
- [Hack The Box — Hathor](https://app.hackthebox.com/machines/hathor)
- [Knowledge — Get-bADpasswords y DCSync](../../../knowledge/windows/badpasswords-dcsync.md)
