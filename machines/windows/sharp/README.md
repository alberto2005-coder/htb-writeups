---
machine: Sharp
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, portablekanban, dotnet-remoting, wcf, ysoserial]
---

# Sharp — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

PortableKanban guarda credenciales descifrables y permite el primer acceso. Un servicio .NET Remoting acepta un payload serializado con `ysoserial.net` y da una shell de usuario. El reversing de un servicio WCF revela un endpoint que ejecuta PowerShell y permite llegar a SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p135,139,445,5985 <IP>
# PortableKanban
PortableKanban.exe
# .NET Remoting
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "calc" -o raw > payload.bin
python3 remoting_client.py <IP> payload.bin
# WCF
dnSpy.exe <SERVICE>.exe
# Endpoint de administración
powershell -c "Invoke-Command -ComputerName <HOST> -ScriptBlock { whoami }"
```

## Enumeración

- PortableKanban con su configuración y base local.
- .NET Remoting expuesto con formateador binario.
- Servicio WCF con un endpoint de administración.

## Acceso inicial

Se localiza la configuración de PortableKanban o su base y se recupera la contraseña almacenada. Con esas credenciales se accede al host y se enumera el servicio .NET Remoting.

## Escalada de privilegios

Se genera un payload `BinaryFormatter` con `ysoserial.net` y se envía al canal remoto, obteniendo ejecución como el usuario del servicio. Se decompila el servicio WCF con dnSpy, se identifica el endpoint que lanza PowerShell y se usa para ejecutar como SYSTEM.

## Evidencia

- Contraseña de PortableKanban descifrada.
- Payload de ysoserial aceptado y shell de usuario.
- Endpoint WCF invocado con PowerShell como SYSTEM.

## Lecciones aprendidas

- Las aplicaciones de escritorio guardan secretos recuperables.
- .NET Remoting con BinaryFormatter es deserialización insegura.
- Los endpoints WCF de administración deben autenticarse y limitarse.

## Mitigación y detección

- No almacenar contraseñas recuperables y rotarlas.
- Eliminar .NET Remoting o migrar a canales seguros.
- Restringir WCF y ejecutar servicios con cuentas de bajo privilegio.

## Referencias

- [0xdf — Sharp](https://0xdf.gitlab.io/2021/05/01/htb-sharp.html)
- [ysoserial.net](https://github.com/pwntester/ysoserial.net)
- [Hack The Box — Sharp](https://app.hackthebox.com/machines/sharp)
