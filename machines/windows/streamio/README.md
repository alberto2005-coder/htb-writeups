---
machine: StreamIO
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, sqli, mssql, lfi, rfi, bloodhound, laps, active-directory]
---

# StreamIO — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`watch.streamio.htb` tiene una SQLi que filtra hashes; las credenciales dan acceso al panel, cuyo parámetro `debug` permite LFI y RFI. La cadena continúa con MSSQL, credenciales guardadas en Firefox, BloodHound y LAPS hasta el administrador del dominio.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,443,445,1433,5985 <IP>
```

El certificado TLS revela `watch.streamio.htb`. Se añaden ambos vhosts al hosts. Se enumeran rutas y subdominios.

## Acceso inicial

`search.php` es inyectable en MSSQL. Se extraen usuarios y hashes:

```bash
sqlmap -r search.txt --batch --dbms=mssql
hashcat -m 0 hashes.txt rockyou.txt
```

Las credenciales crackeadas permiten entrar en `streamio.htb/login.php`.

## LFI y RCE

El panel de administración acepta `?debug=`. Se usa un wrapper PHP para leer el código fuente:

```bash
curl 'https://streamio.htb/admin/?debug=php://filter/convert.base64-encode/resource=index.php'
```

El código revela credenciales de `db_admin` y un parámetro `include` vulnerable a RFI. Se aloja un PHP y se incluye para obtener una shell.

## Movimiento lateral

```powershell
sqlcmd -S localhost -U db_admin -P '<password>'
```

Se enumeran bases y se extrae una copia de seguridad con credenciales de otro usuario. Se accede por WinRM. En el perfil de Firefox hay credenciales guardadas que se reutilizan en el dominio.

## Escalada a administrador

Se ejecuta BloodHound y se identifica que el usuario puede añadirse a un grupo con `ReadLAPSPassword`. Se abusa de esa capacidad para leer la contraseña LAPS del controlador de dominio:

```powershell
bloodyAD --host dc.streamio.htb -d streamio.htb -u <user> -p '<password>' add groupMember 'CORE STAFF' <user>
```

Con la contraseña LAPS se accede como administrador y se lee la flag.

## Evidencia

- SQLi y hashes redactados.
- LFI con el código fuente.
- Credenciales MSSQL y backup redactados.
- Salida de BloodHound y LAPS redactada.

## Lecciones aprendidas

- Una SQLi en un subdominio puede comprometer todo el dominio.
- El parámetro `debug` y los includes dinámicos son RCE.
- Las credenciales de navegador se reutilizan.
- LAPS mal delegado entrega la contraseña local del DC.

## Mitigación y detección

- Parametrizar consultas y limitar errores SQL.
- Eliminar parámetros de depuración en producción.
- Restringir `include` a rutas permitidas.
- Auditar delegación de LAPS y grupos privilegiados.

## Referencias

- <https://www.hackthebox.com/machines/streamio>
- <https://bloodhound.readthedocs.io/>
- <https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview>
