---
machine: Silentium
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, flowise, password-reset, docker, gogs, symlink]
---

# Silentium — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El subdominio de staging ejecuta Flowise. El endpoint de recuperación devuelve el token en la respuesta y permite tomar la cuenta de `ben`; la versión 3.0.5 es vulnerable a CVE-2025-59528 y ejecuta código como root en el contenedor. Las variables de entorno filtran una contraseña reutilizada por `ben` en SSH. En el host, Gogs 0.13.3 permite CVE-2025-8110 y, mediante un symlink, escribe una clave en `/root/.ssh`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<DOMAIN> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeración

- `staging.silentium.htb` muestra un login de Flowise y la API revela la versión 3.0.5.
- El reset de contraseña devuelve el token en el cuerpo de la respuesta.
- En el host, Gogs 0.13.3 escucha en `127.0.0.1:3001` y se ejecuta como root.

## Acceso inicial

Se enumera un correo válido con el reset y se usa el token devuelto para cambiar la contraseña de `ben`. Ya autenticado, se abusa de un nodo que pasa configuración al constructor `Function` de JavaScript (CVE-2025-59528) y se ejecuta código como root dentro del contenedor. Las variables de entorno contienen la contraseña de `ben`, reutilizada en SSH.

## Escalada de privilegios

Como `ben` se accede a Gogs en localhost. CVE-2025-8110 permite crear un repositorio con un symlink a `/root/.ssh` y usar la API `PutContents` para escribir `authorized_keys` fuera del repositorio. La escritura ocurre antes de que falle el commit, así que se entra por SSH como root.

## Evidencia

- Respuesta del reset con el token y sesión de `ben`.
- Ejecución en el contenedor y `hostname` de Docker.
- Symlink en Gogs y acceso SSH como root.

## Lecciones aprendidas

- Nunca devolver tokens de recuperación en la respuesta.
- Los constructores dinámicos convierten configuración en ejecución de código.
- La validación de rutas debe resolver symlinks antes de escribir.

## Mitigación y detección

- Enviar tokens solo por un canal seguro y de un solo uso.
- Aislar nodos y deshabilitar `Function` con entrada de usuario.
- Resolver rutas con `realpath` y confinar escrituras al repositorio.

## Referencias

- [0xdf — Silentium](https://0xdf.gitlab.io/2026/09/12/htb-silentium.html)
- [IppSec — Silentium](https://www.youtube.com/watch?v=B9lVpmiCORQ)
- [Hack The Box — Silentium](https://app.hackthebox.com/machines/silentium)
