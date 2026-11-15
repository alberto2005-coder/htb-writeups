---
machine: Hancliffe
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, uri-parsing, nuxeo, ssti, universal-remote, buffer-overflow, socket-reuse]
---

# Hancliffe — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un fallo de parseo de URI da acceso a un Nuxeo interno, vulnerable a SSTI de Java y RCE. Desde ahí se llega a Universal Remote, que ejecuta comandos como el siguiente usuario. Un password guardado en Firefox permite pasar a otro usuario, y una aplicación de desarrollo en 9999 tiene un buffer overflow con reutilización de socket que acaba en Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,8000,9999 <IP>
```

- `80` nginx, `8000` HashPass y `9999` una aplicación bancaria.
- `80` redirige a `hancliffe.htb`.
- `feroxbuster` enumera rutas y parámetros.

## Enumeración

- El portal usa un parser de URI que permite confundir el host y alcanzar un Nuxeo interno.
- Nuxeo expone una plantilla Java; una expresión SSTI ejecuta comandos.
- La aplicación de `9999` se identifica como Universal Remote y permite ejecutar comandos como el usuario que la ejecuta.

## Foothold

Se explota la SSTI de Nuxeo para obtener una shell y se enumera el host. Desde esa shell se accede a Universal Remote y se ejecuta una reverse shell como el siguiente usuario.

```text
${7*7}
```

## Movimiento lateral

En el perfil de Firefox hay una contraseña guardada para `H@$hPa$$`; `firepwd` la extrae y permite `su` al siguiente usuario. Ese usuario tiene acceso a la aplicación de desarrollo de `9999`.

## Escalada de privilegios

La aplicación `MyFirstApp.exe` en `9999` tiene un buffer overflow. Se usa un patrón para el offset, un `JMP ESP`, shellcode y reutilización del socket para leer la segunda etapa. El proceso corre como Administrator y la shell final es de Administrator.

```text
python3 exploit.py <IP> 9999
```

## Evidencia

- URI parsing y Nuxeo interno.
- SSTI Java y shell inicial.
- Universal Remote y siguiente usuario.
- Firefox `firepwd` y credenciales.
- Buffer overflow con socket reuse y Administrator.

## Lecciones aprendidas

- Un parser de URI permisivo puede saltarse reglas de host.
- Nuxeo con plantillas Java es SSTI/RCE.
- Universal Remote es ejecución remota por diseño.
- Los perfiles de Firefox guardan credenciales de sistema.

## Mitigación y detección

- Validar URIs y bloquear destinos internos.
- Actualizar Nuxeo y deshabilitar plantillas no confiables.
- Restringir Universal Remote y ejecutarlo con mínimo privilegio.
- Proteger perfiles de navegador y aplicar ASLR/DEP; revisar binarios de desarrollo.

## Referencias

- [0xdf — Hancliffe](https://0xdf.gitlab.io/2022/03/05/htb-hancliffe.html)
- [IppSec — Hancliffe](https://www.youtube.com/watch?v=kA-bkftyyY0)
- [Hack The Box — Hancliffe](https://app.hackthebox.com/machines/hancliffe)
