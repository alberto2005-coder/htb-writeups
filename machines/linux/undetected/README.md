---
machine: Undetected
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, phpunit, cve-2017-9841, apache, backdoor, sshd, reversing, privesc]
---

# Undetected — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El vhost `store.djewelry.htb` expone `vendor/composer/installed.json`, que revela PHPUnit 5.6.2. `eval-stdin.php` permite ejecutar PHP sin autenticación (CVE-2017-9841) y da `www-data`. Un binario en `/var/backups` muestra que un atacante anterior añadió usuarios `*1` a `/etc/passwd` y `/etc/shadow`; el hash se crackea y da `steven1`. El módulo Apache `mod_reader.so` descarga un sshd backdooreado con una contraseña XOR, que al revertirla da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.2 y `80` Apache 2.4.41 en Ubuntu 20.04.
- `index.php` devuelve 404; `index.html` es la portada.
- El vhost `store.djewelry.htb` se descubre por fuzzing de subdominios.

## Enumeración

`/vendor/composer/installed.json` lista las dependencias y confirma PHPUnit 5.6.2. Se busca la versión y aparece CVE-2017-9841: `vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php` evalúa el cuerpo POST.

## Foothold

Se envía `<?php system("id"); ?>` al endpoint y se confirma ejecución. Una reverse shell con base64 evita problemas de caracteres y devuelve `www-data`. En `/var/backups` hay un binario `info` que, al revertirlo, muestra que un atacante anterior añadió usuarios `<user>1` con UID duplicado y un hash fijo a `/etc/shadow`.

```bash
# PHPUnit
curl 'http://store.djewelry.htb/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php' \
  -d '<?php system("id"); ?>'
# hash y sshd
hashcat -m 1800 steven1.hash rockyou.txt
python3 backdoor_sshd.py
ssh root@<IP>
```

## Movimiento lateral

El usuario `steven1` ya existe con el mismo UID que `steven`. El hash de `/etc/shadow` se crackea con hashcat modo 1800 y la contraseña permite SSH como `steven1`, no como `steven`.

## Escalada de privilegios

`/usr/lib/apache2/modules/mod_reader.so` y `reader.load` fueron modificados por el atacante. El módulo ejecuta un `wget` de `sharefiles.xyz/image.jpeg` sobre `/usr/sbin/sshd`; el binario resultante tiene una puerta trasera en `auth_password` que compara la contraseña con 31 bytes XOR 0x96. Se extraen los bytes, se invierte el XOR y se entra como root.

## Evidencia

- `installed.json` con PHPUnit 5.6.2.
- `eval-stdin.php` y shell `www-data`.
- Usuarios `*1` y hash de `steven1`.
- `mod_reader.so` y sshd con contraseña XOR.

## Lecciones aprendidas

- Las dependencias de desarrollo no deben quedar en producción.
- Un binario de backup puede documentar el ataque anterior.
- Los usuarios con UID duplicado ocultan puertas traseras.
- Los módulos Apache y binarios modificados sobreviven a la limpieza superficial.

## Mitigación y detección

- Eliminar `vendor` de desarrollo y bloquear `eval-stdin.php`.
- Auditar `/etc/passwd`, `/etc/shadow` y UIDs duplicados.
- Verificar módulos Apache y binarios del sistema.
- Monitorizar descargas y cambios en `/usr/sbin/sshd`.

## Referencias

- [0xdf — Undetected](https://0xdf.gitlab.io/2022/07/02/htb-undetected.html)
- [IppSec — Undetected](https://www.youtube.com/watch?v=TNwZAacbQs4)
- [Hack The Box — Undetected](https://app.hackthebox.com/machines/undetected)
