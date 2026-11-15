---
machine: Dog
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, backdrop-cms, git, module-upload, bee, privesc]
---

# Dog — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un repositorio `.git` expuesto en Backdrop CMS filtra `settings.php` y credenciales de base. Con la cuenta `tiffany` se sube un módulo malicioso y se obtiene `www-data`; una contraseña compartida permite pasar a `johncusack`. Ese usuario puede ejecutar `bee` como root, y `bee eval` ejecuta PHP arbitrario, incluida una shell de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con Backdrop CMS.
- `nmap` detecta `http-git` y `feroxbuster` confirma `/.git/`.
- `robots.txt` lista rutas de administración.

## Enumeración

`git-dumper` reconstruye el repositorio. `settings.php` contiene la cadena de conexión MySQL y el usuario `tiffany` aparece en la configuración.

```bash
git-dumper http://dog.htb/.git dog-src
grep -R "mysql://" dog-src
```

## Foothold

Con `tiffany` se entra al panel de Backdrop y se sube un módulo malicioso. El módulo incluye un webshell PHP que se ejecuta al visitarlo y da `www-data`.

```bash
curl 'http://dog.htb/modules/<MODULE>/shell.php?cmd=id'
```

## Movimiento lateral

La contraseña de la base también funciona para `johncusack` en el sistema.

```bash
su johncusack
```

## Escalada de privilegios

`johncusack` puede ejecutar `bee` como root. `bee eval` evalúa PHP en el contexto de la instalación; `system("bash")` devuelve una shell de root.

```bash
sudo bee eval 'system("bash")'
```

## Evidencia

- `.git` expuesto y `settings.php`.
- Credenciales de `tiffany`.
- Módulo malicioso y `www-data`.
- Contraseña compartida y `johncusack`.
- `bee eval` y root.

## Lecciones aprendidas

- Un `.git` expuesto filtra configuración y credenciales.
- Los CMS permiten subir módulos, que son código ejecutable.
- Las contraseñas de base se reutilizan con demasiada frecuencia.
- Una herramienta de administración con `eval` es ejecución como su usuario.

## Mitigación y detección

- No publicar `.git` y rotar credenciales si se expone.
- Validar y firmar módulos; limitar la subida a administradores.
- Separar contraseñas de base y sistema.
- No permitir `bee eval` como root; usar un wrapper con comandos permitidos.

## Referencias

- [0xdf — Dog](https://0xdf.gitlab.io/2025/07/12/htb-dog.html)
- [IppSec — Dog](https://www.youtube.com/watch?v=Z24FN8qqngY)
- [Hack The Box — Dog](https://app.hackthebox.com/machines/dog)
