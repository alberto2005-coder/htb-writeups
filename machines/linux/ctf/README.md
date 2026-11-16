---
machine: CTF
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, ldap-injection, otp, second-order, 7z, privesc]
---

# CTF — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web usa LDAP para autenticar con usuario y OTP. Una inyección LDAP con doble URL-encoding filtra el usuario y la semilla del token; `stoken` genera el OTP y una inyección de segundo orden salta la comprobación. El código de `page.php` filtra la contraseña de `ldapuser`, y un backup con `7za` y wildcard permite leer el flag de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con PHP 5.4 en CentOS 7.
- La portada advierte de un baneo temporal si se generan muchos 404.
- `/status.php` muestra el estado y las IPs bloqueadas; el login pide usuario y OTP.

## Enumeración

El HTML del login revela que el token se guarda en un atributo LDAP existente. Se doble codifica `*` como `%252a`; el usuario empieza por `l` y se puede extraer carácter a carácter. Después se enumeran atributos candidatos (`mail`, `pager`, `userPassword`) y se filtra la semilla del OTP con `ldapuser)(<ATTR>=<valor>*`.

## Foothold

Con la semilla y el desfase horario del servidor, `stoken` genera el OTP. El primer login lleva a `page.php`, pero el comando se rechaza; se repite el login con `ldapuser)))%00` para una inyección de segundo orden que salta la comprobación. El código de la página se descarga en base64 y contiene `$password` para SSH.

```bash
# login LDAP con doble encoding y OTP
curl -s http://<IP>/login.php --data 'inputUsername=ldapuser%2529%2529%2529%2500&inputOTP=<OTP>'
# backup wildcard
touch @lista; ln -fs /root/root.txt lista
```

## Movimiento lateral

No hay pivote adicional: `ldapuser` entra por SSH y el siguiente objetivo es el script de backup que corre como root.

## Escalada de privilegios

`/backup/backup.sh` ejecuta `7za a /backup/$filename.zip -t7z -snl -p$pass -- *` cada minuto. En el directorio escribible se crea `@lista` y un symlink `lista` a `/root/root.txt`; `7za` interpreta `@lista` como lista de archivos y el error incluye el contenido del destino. También se puede seguir el log con `tail -f` antes de que el script lo borre.

## Evidencia

- Usuario y semilla OTP extraídos por LDAP injection.
- `stoken` y login de segundo orden.
- Contraseña en el código de `page.php`.
- Backup `7za` con wildcard y lectura de root.

## Lecciones aprendidas

- La doble codificación puede saltar filtros de caracteres LDAP.
- Guardar el OTP en un atributo legible amplía el impacto.
- Una comprobación de usuario en dos fases puede ser inyectable en la segunda.
- Los wildcards en scripts root convierten nombres de archivo en argumentos.

## Mitigación y detección

- Parametrizar las consultas LDAP y escapar metacaracteres.
- No reutilizar atributos existentes para secretos.
- Evitar wildcards; usar `find -print0` y `xargs -0`.
- Vigilar archivos `@*` y errores de `7za` en backups.

## Referencias

- [0xdf — CTF](https://0xdf.gitlab.io/2019/07/20/htb-ctf.html)
- [IppSec — CTF](https://www.youtube.com/watch?v=51JQg202csw)
- [Hack The Box — CTF](https://app.hackthebox.com/machines/ctf)
