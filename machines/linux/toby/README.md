---
machine: Toby
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, php, backdoor, mysql, gogs, pam, privesc]
---

# Toby — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Toby sigue los pasos de un atacante anterior: un webshell PHP ofuscado se carga desde el tema de WordPress y se comunica con un parámetro concreto. Desde ahí se pivota a un contenedor MySQL, se crackean hashes y se entra en Gogs. El código y un generador de contraseñas permiten pasar a la host como `jack`; un PAM backdoor con contraseña de diez caracteres se descubre en un ticket y se fuerza por temporización hasta root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con WordPress y un vhost `gogs.toby.htb`.
- `wpscan` enumera plugins y temas; el tema activo tiene un archivo PHP sospechoso.
- `gobuster` encuentra `/wp-content/themes/<THEME>/`.

## Enumeración

- El tema incluye un webshell ofuscado; el código muestra que espera un parámetro y una clave.
- Se desofusca con CyberChef o `php -r` y se identifica el parámetro de ejecución.
- El webshell se comunica con un contenedor MySQL interno.

```bash
curl 'http://toby.htb/wp-content/themes/<THEME>/<FILE>.php?<PARAM>=id'
```

## Foothold

Con el webshell se ejecuta una reverse shell como `www-data`. La enumeración muestra un contenedor MySQL y credenciales en la configuración de WordPress.

```bash
mysqldump -u <USER> -p'<PASSWORD>' --all-databases > /tmp/db.sql
```

## Movimiento lateral

La base contiene hashes de Gogs y de usuarios del sistema. Se crackean y se accede a Gogs como `toby-admin`; el repositorio `supportsystem-db` incluye un generador de contraseñas y el código de soporte. Con el generador se produce una lista y se crackea el hash de `jack`; su contraseña funciona en el contenedor MySQL y en la host por SSH.

```bash
hashcat -m 11200 jack.hash passwordlist
ssh jack@toby.htb
```

## Escalada de privilegios

El ticket de soporte menciona un módulo PAM modificado. En `/lib/security` hay un `.so` con fecha anómala; Ghidra muestra que compara una contraseña de diez caracteres con una comparación que tarda más cuanto más prefijo coincide. Un script mide el tiempo de `su` y recupera la contraseña carácter a carácter; con ella se entra como root.

```bash
for c in 0 1 2 3 4 5 6 7 8 9; do printf '%s' "$candidate$c" | timeout 2 su -c true root; done
```

## Evidencia

- Webshell ofuscado en el tema y parámetro secreto.
- Contenedor MySQL y hashes.
- Gogs, generador de contraseñas y `jack`.
- Módulo PAM con contraseña de diez caracteres.
- Ataque de temporización y root.

## Lecciones aprendidas

- Un tema de WordPress puede ocultar un webshell que solo responde a un parámetro concreto.
- Los contenedores internos amplían la superficie y filtran bases de datos.
- Un generador de contraseñas en un repositorio reduce el espacio de búsqueda.
- Una comparación no constante en PAM permite recuperar la contraseña por tiempo.

## Mitigación y detección

- Auditar temas y plugins; comparar archivos con el código oficial.
- Aislar contenedores y no reutilizar credenciales entre servicios.
- Revisar módulos PAM y fechas de modificación inusuales.
- Usar comparaciones constantes y limitar los intentos de autenticación.

## Referencias

- [0xdf — Toby](https://0xdf.gitlab.io/2022/04/16/htb-toby.html)
- [IppSec — Toby](https://www.youtube.com/watch?v=XROkuXKgeg8)
- [Hack The Box — Toby](https://app.hackthebox.com/machines/toby)
