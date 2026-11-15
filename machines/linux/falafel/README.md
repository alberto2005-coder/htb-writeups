---
machine: Falafel
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, sqli, type-juggling, magic-hash, debugfs]
---

# Falafel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El login usa comparaciones débiles y un hash mágico permite entrar como admin. La subida de archivos da una shell; la escalada lee la pantalla desde `/dev/fb0` y usa `debugfs` sobre el disco para llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
sqlmap -u "http://falafel.htb/login.php" --data="username=admin&password=test" --batch
# Hash mágico para el bypass
curl -d "username=admin&password=240610708" http://falafel.htb/login.php
# Tras la shell
id; groups
cat /dev/fb0 > /tmp/fb.raw
debugfs -R "cat /root/root.txt" /dev/sdb1
```

## Enumeración

- Login PHP con comparación débil de hashes.
- Formulario de subida y una aplicación de gestión de usuarios.
- El usuario pertenece a grupos con acceso a dispositivos de bloque.

## Acceso inicial

La contraseña `240610708` produce un hash MD5 que empieza por `0e` y la comparación lo trata como cero. Se entra como admin, se sube un archivo PHP y se obtiene ejecución como `www-data`.

## Escalada de privilegios

La aplicación muestra credenciales de otro usuario. Con esa cuenta se lee `/dev/fb0` para recuperar la pantalla y una contraseña; el grupo de disco permite usar `debugfs` sobre la partición y leer archivos de root.

## Evidencia

- Hash mágico aceptado por el login.
- Subida de PHP y shell como `www-data`.
- Lectura de `/dev/fb0` y `debugfs` sobre el disco.

## Lecciones aprendidas

- Las comparaciones `==` con hashes pueden colapsar a cero.
- Los dispositivos de bloque accesibles son equivalentes a root.
- La información en pantalla puede contener secretos.

## Mitigación y detección

- Usar `password_verify` y comparaciones estrictas.
- Restringir el acceso a `/dev/fb0` y a los dispositivos de bloque.
- Validar extensiones y permisos de subida.

## Referencias

- [0xdf — Falafel](https://0xdf.gitlab.io/2018/06/23/htb-falafel.html)
- [PHP — Type juggling](https://www.php.net/manual/en/language.types.type-juggling.php)
- [Hack The Box — Falafel](https://app.hackthebox.com/machines/falafel)
