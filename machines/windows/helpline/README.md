---
machine: Helpline
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, manageengine, servicedesk, xxe, lfi, winrm, efs, privesc]
---

# Helpline — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

ManageEngine ServiceDesk Plus acepta la cuenta invitada y filtra un Excel con una auditoría de contraseñas. Un XXE (CVE-2017-9362) lee `it_logins.txt` y da acceso a `alice` por WinRM; desde ahí se encadenan credenciales en logs y archivos hasta `leo` y un administrador. En paralelo, el LFI CVE-2017-11511 y el panel de SDP permiten llegar a SYSTEM; los archivos sensibles están protegidos con EFS y se descifran con Mimikatz.

## Reconocimiento

```bash
nmap -Pn -sCV -p135,445,5985,8080 <IP>
```

- `8080` ManageEngine ServiceDesk Plus.
- `5985` WinRM, `445` SMB y `135` RPC.
- El host es Windows y el panel usa autenticación local.

## Enumeración

La cuenta por defecto `guest:guest` funciona. En la sección de soluciones hay un Excel de auditoría de contraseñas con usuarios y una referencia a `C:\Temp\Password Audit\it_logins.txt`.

## Foothold

Se explota XXE en la API de SDP (CVE-2017-9362) para leer `it_logins.txt` y obtener credenciales de `alice`. Con ellas se entra por WinRM.

```bash
python3 mesep_xxe.py <IP> "C:\temp\Password Audit\it_logins.txt"
```

## Movimiento lateral

Desde `alice` se revisan logs de eventos y archivos accesibles; aparecen credenciales de `zachary` y después de `tolu`. `tolu` accede a la unidad `E:`, donde un script de PowerShell se puede inyectar para obtener `leo`. En el escritorio de `leo` hay credenciales de administrador en XML.

## Escalada de privilegios

La otra vía usa el LFI CVE-2017-11511 para descargar archivos del panel y llegar a la base de SDP. Como administrador de SDP se modifica la contraseña en PostgreSQL y se abusa de un trigger para ejecutar como SYSTEM. Los archivos importantes están cifrados con EFS; Mimikatz/`crypto` descifran las claves y permiten leer los flags.

## Evidencia

- `guest:guest` y auditoría de contraseñas.
- XXE CVE-2017-9362 y `alice`.
- Logs/credenciales hasta `tolu` y `leo`.
- LFI CVE-2017-11511 y panel SDP.
- Trigger PostgreSQL, SYSTEM y EFS.

## Lecciones aprendidas

- Las cuentas de invitado de paneles antiguos siguen siendo útiles.
- Un XXE puede leer archivos internos y credenciales.
- Los logs de eventos y backups de TI acumulan secretos.
- EFS no protege si el atacante obtiene SYSTEM y las claves.
- Un trigger de base de datos puede ejecutar código.

## Mitigación y detección

- Deshabilitar cuentas invitado y cambiar credenciales por defecto.
- Actualizar ServiceDesk Plus y deshabilitar XXE.
- Restringir WinRM y auditar el acceso a logs.
- Proteger EFS con cuentas separadas y rotar secretos.
- Revisar triggers y permisos de PostgreSQL.

## Referencias

- [0xdf — Helpline](https://0xdf.gitlab.io/2019/08/17/htb-helpline.html)
- [IppSec — Helpline](https://www.youtube.com/watch?v=Vs3oSDlzxwA)
- [Hack The Box — Helpline](https://app.hackthebox.com/machines/helpline)
