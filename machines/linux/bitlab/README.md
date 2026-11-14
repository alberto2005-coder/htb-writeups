---
machine: Bitlab
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitlab, webshell, postgresql, reversing]
---

# Bitlab — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

GitLab Community Edition filtra credenciales en la página de login. Con la sesión de `clave` se publica una webshell en un proyecto y se obtiene `www-data`; un túnel a PostgreSQL revela la contraseña de `clave`. En su home, `RemoteConnection.exe` contiene la contraseña de root usada para `putty`, lo que permite el acceso final.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://<IP>/FUZZ
```

## Enumeración

- La web ejecuta GitLab CE y muestra proyectos de `root`.
- El HTML de login filtra credenciales de `clave`.
- El host escucha PostgreSQL en 5432; hay contenedores GitLab y PostgreSQL.

## Acceso inicial

Se inicia sesión en GitLab con las credenciales filtradas y se crea o modifica un proyecto con una webshell. Al confirmar el cambio, el servidor la interpreta y ejecuta como `www-data`.

## Escalada de privilegios

Se abre un túnel SSH para llegar a PostgreSQL, se consultan usuarios y se recupera la contraseña de `clave`. En su home aparece `RemoteConnection.exe`, que lanza `putty` con `-pw`; el análisis con `strings`, IDA y `x32dbg` revela la contraseña de root, válida por SSH.

## Evidencia

- Credenciales visibles en el HTML de GitLab.
- Commit con la webshell y ejecución como `www-data`.
- Cadena `putty -pw` en memoria y acceso SSH como root.

## Lecciones aprendidas

- El código fuente y el HTML pueden filtrar secretos.
- Los túneles SSH convierten servicios internos en accesibles.
- Los binarios de escritorio pueden contener credenciales en texto claro.

## Mitigación y detección

- Rotar credenciales expuestas y revisar el HTML generado.
- Aislar GitLab y PostgreSQL; no reutilizar contraseñas.
- No guardar secretos en binarios ni en argumentos de proceso.

## Referencias

- [0xdf — Bitlab](https://0xdf.gitlab.io/2020/01/11/htb-bitlab.html)
- [IppSec — Bitlab](https://www.youtube.com/watch?v=Fxq6oZ-H-xI)
- [Hack The Box — Bitlab](https://app.hackthebox.com/machines/bitlab)
