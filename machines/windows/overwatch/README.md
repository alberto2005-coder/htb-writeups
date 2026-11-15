---
machine: Overwatch
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, smb, dotnet, mssql, wcf, dns, privesc]
---

# Overwatch — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un share SMB anónimo contiene un binario .NET de monitorización. La ingeniería inversa recupera credenciales de MSSQL y un servicio WCF con un sink de command injection. Un linked server apunta a un host que no resuelve; `CREATE_CHILD` sobre la zona DNS de AD permite añadir un registro, capturar la autenticación SQL con Responder y entrar por WinRM. El comando `KillProcess` del WCF en localhost ejecuta como SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,3268,3389,5985,6520,9389 <IP>
```

- El host es un DC de `overwatch.htb` con SMB, LDAP, Kerberos, RDP y WinRM.
- `6520` es una instancia de MSSQL 2022.
- `netexec smb <IP> -u guest -p '' --shares` muestra un share de software con acceso anónimo.

## Enumeración

- El share contiene `Monitor.exe`, una herramienta .NET de monitorización.
- `dotPeek` muestra credenciales de SQL Server y la URL del servicio WCF.
- El WCF expone `KillProcess`, que pasa el nombre del proceso a PowerShell.

```bash
smbclient //<IP>/Software -N
dotpeek Monitor.exe
```

## Foothold

Con las credenciales de MSSQL se enumeran linked servers. Uno apunta a un nombre que no resuelve; la cuenta tiene `CREATE_CHILD` sobre la zona DNS integrada en AD. Se añade un registro A hacia el atacante y se levanta Responder para capturar la autenticación SQL en claro cuando el linked server se conecta.

```sql
EXEC sp_linkedservers;
EXEC ('SELECT 1') AT [LINKED];
```

## Movimiento lateral

Las credenciales capturadas pertenecen a un usuario de `Remote Management Users`; WinRM da shell. Desde ahí se enumera el WCF en localhost y se identifican los métodos y el formato SOAP.

```bash
evil-winrm -i <IP> -u <USER> -p '<PASSWORD>'
```

## Escalada de privilegios

El método `KillProcess` se invoca por SOAP contra `localhost:8000`; el parámetro se concatena en un comando de PowerShell que corre como SYSTEM. Se envía una reverse shell o se añade el usuario a Administrators.

```text
POST /MonitorService/ HTTP/1.1
SOAPAction: "http://tempuri.org/IMonitoringService/KillProcess"
<processName>x; powershell -e <BASE64>; #</processName>
```

## Evidencia

- Share SMB anónimo y binario .NET.
- Credenciales MSSQL y linked server.
- Registro DNS añadido y captura con Responder.
- WinRM como usuario de gestión.
- WCF `KillProcess` y SYSTEM.

## Lecciones aprendidas

- Un share anónimo con binarios internos filtra credenciales y contratos.
- Un linked server que no resuelve se puede redirigir controlando DNS.
- `CREATE_CHILD` en una zona AD integrada permite secuestrar nombres.
- Un WCF local con command injection es SYSTEM si el servicio corre como SYSTEM.

## Mitigación y detección

- Cerrar el acceso anónimo a shares y no guardar credenciales en binarios.
- Restringir `CREATE_CHILD` y auditar cambios en zonas DNS.
- Firmar y validar la autenticación SQL; no enviar credenciales en claro.
- Parametrizar el WCF y ejecutarlo con una cuenta de servicio de mínimo privilegio.

## Referencias

- [0xdf — Overwatch](https://0xdf.gitlab.io/2026/05/09/htb-overwatch.html)
- [IppSec — Overwatch](https://www.youtube.com/watch?v=zOK_EzOyMN0)
- [Hack The Box — Overwatch](https://app.hackthebox.com/machines/overwatch)
