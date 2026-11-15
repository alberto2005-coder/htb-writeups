---
machine: Charon
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, rsa, suid, privesc]
---

# Charon — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El formulario de recuperación de contraseña es inyectable. Un bypass del filtro de `UNION` y `GROUP_CONCAT` permite volcar usuarios y hashes MD5; con el usuario `decoder` se sube un webshell al CMS. En su home hay una clave pública RSA con módulo pequeño y `pass.crypt`; al factorizar el módulo se descifra la contraseña y se entra por SSH. Un SUID `supershell` pasa su argumento a `system`, así que una sustitución de comandos ejecuta código como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH y `80/tcp` Apache con un CMS de noticias.
- `gobuster` encuentra `/cmsdata/` y el formulario `forgot.php`.
- La web usa PHP y una base MySQL.

## Enumeración

- `forgot.php` refleja el resultado de la consulta: un `'` produce un error de base.
- El filtro bloquea `UNION` en mayúsculas; `UNiON` lo evade.
- La consulta devuelve cuatro columnas y la cuarta debe ser un email válido.

## Foothold

Se usa `UNION SELECT 1,group_concat(concat(__username_,':',__password_)),3,'a@b.c' from operators` para volcar usuarios y hashes. Los MD5 se crackean y `decoder` permite entrar al CMS. El CMS tiene un uploader de imágenes que acepta PHP si se cambia la extensión y el tipo MIME.

```bash
curl -s http://<IP>/cmsdata/forgot.php --data-urlencode "email=a@b.c' UNiON SELECT 1,group_concat(concat(__username_,':',__password_)),3,'a@b.c' from operators;-- -"
```

## Movimiento lateral

La shell es `www-data`. En `/home/decoder` hay `decoder.pub`, `pass.crypt` y la flag de usuario. El módulo RSA es demasiado pequeño: se factoriza, se calcula `d` y se descifra `pass.crypt` para obtener la contraseña de `decoder`, que funciona por SSH.

```python
from Crypto.PublicKey import RSA
key = RSA.importKey(open("decoder.pub").read())
# factorizar key.n y calcular d
```

## Escalada de privilegios

`find / -perm -4000` muestra `supershell`, propiedad de root y con SUID. El binario ejecuta `system()` sobre su argumento; se puede inyectar una sustitución de comandos para copiar una clave o lanzar una shell.

```bash
supershell '/bin/ls $(cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash)'
/tmp/rootbash -p
```

## Evidencia

- Error de SQLi y bypass `UNiON`.
- Usuarios y hashes volcados; acceso al CMS como `decoder`.
- Clave RSA de módulo pequeño y `pass.crypt` descifrado.
- SUID `supershell` y ejecución con sustitución de comandos.

## Lecciones aprendidas

- Los filtros que solo buscan mayúsculas se evitan cambiando el caso.
- RSA con módulos pequeños se factoriza en segundos.
- Un SUID que llama a `system` con entrada del usuario es ejecución root directa.

## Mitigación y detección

- Usar consultas parametrizadas y validar el email en servidor.
- Emplear RSA de al menos 2048 bits y no cifrar secretos con clave pública débil.
- Evitar SUID innecesarios y no pasar argumentos a `system`.

## Referencias

- [0xdf — Charon](https://0xdf.gitlab.io/2021/02/16/htb-charon.html)
- [IppSec — Charon](https://www.youtube.com/watch?v=_csbKuOlmdE)
- [Hack The Box — Charon](https://app.hackthebox.com/machines/charon)
