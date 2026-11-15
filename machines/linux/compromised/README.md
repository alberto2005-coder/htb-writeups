---
machine: Compromised
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, litecart, php, disable-functions, pam, backdoor, privesc]
---

# Compromised — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La caja ya está comprometida: un backup de LiteCart muestra un login backdoored que escribe credenciales en un archivo accesible. Con esas credenciales se explota LiteCart, pero `disable_functions` bloquea la ejecución; se rodea con el propio MySQL y un UDF, y el usuario `mysql` tiene shell. Un `strace` actúa de keylogger y entrega la contraseña de `sysadmin`. Para root quedan dos backdoors: un módulo PAM y un `LD_PRELOAD` en un SUID.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con LiteCart en `/shop`.
- El site está en producción pero mantiene un backup accesible.
- `gobuster` encuentra `/shop/admin/` y archivos de backup.

## Enumeración

- El backup contiene el código de `login.php` modificado: registra usuario y contraseña en un archivo dentro del webroot.
- Se lee ese archivo y se obtienen credenciales de administrador.
- `searchsploit litecart` muestra el RCE de subida de módulos.

## Foothold

Se sube un módulo XML/PHP malicioso, pero `disable_functions` bloquea `system`, `exec` y similares. Se usa una cuenta MySQL con privilegios para crear un UDF y ejecutar comandos; el usuario `mysql` tiene una shell válida.

```sql
CREATE FUNCTION sys_exec RETURNS int SONAME 'lib_mysqludf_sys.so';
SELECT sys_exec('id');
```

## Movimiento lateral

En `/var/log` o en un archivo de `strace` aparece la ejecución de `mysql` con la contraseña en la línea de comandos. Esa contraseña pertenece a `sysadmin` y funciona también por SSH.

```bash
grep -a 'mysql' /var/log/* 2>/dev/null
ssh sysadmin@<IP>
```

## Escalada de privilegios

El atacante anterior dejó dos puertas: un módulo PAM con una contraseña maestra y un `LD_PRELOAD` en un binario SUID. El módulo PAM acepta una cadena concreta para cualquier usuario, incluido root.

```bash
strings /lib/security/pam_unix.so | grep -i backdoor
```

La alternativa es usar la cadena mágica del `LD_PRELOAD` como contraseña actual de `passwd`; el binario SUID la interpreta y lanza una shell sin bajar privilegios.

## Evidencia

- Backup de LiteCart con login backdoored.
- Credenciales en un archivo del webroot.
- `disable_functions` y UDF de MySQL.
- Contraseña de `sysadmin` en el log de `strace`.
- Módulo PAM y `LD_PRELOAD` como root.

## Lecciones aprendidas

- Un backup público puede contener el código vulnerable y backdoors.
- `disable_functions` no impide RCE si la base de datos puede cargar UDF.
- Los logs de `strace` y los historiales filtran credenciales.
- Una caja comprometida puede tener varias puertas traseras; hay que buscarlas.

## Mitigación y detección

- No dejar backups ni archivos de log dentro del webroot.
- Restringir `CREATE FUNCTION` y los privilegios de MySQL.
- Auditar módulos PAM y binarios SUID con `LD_PRELOAD`.
- Rotar credenciales y reconstruir el host tras una intrusión confirmada.

## Referencias

- [0xdf — Compromised](https://0xdf.gitlab.io/2021/01/23/htb-compromised.html)
- [IppSec — Compromised](https://www.youtube.com/watch?v=yaV09XCDDqI)
- [Hack The Box — Compromised](https://app.hackthebox.com/machines/compromised)
