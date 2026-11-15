---
machine: RustyKey
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, timeroasting, rbcd, 7zip]
---

# RustyKey — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Escenario assume breach con una cuenta AD de bajo privilegio. El análisis de ACL y grupos permite escribir un SPN y hacer Timeroasting; el secuestro de la extensión de 7-Zip da movimiento lateral y RBCD contra el DC lleva a administrador.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,389,445,5985 <IP>
nxc smb <DC> -u <USER> -p "<PASS>" --shares
bloodhound-python -u <USER> -p "<PASS>" -d rustykey.htb -c All
timeroast.py -d rustykey.htb -u <USER> -p "<PASS>"
# 7-Zip y RBCD
Rubeus.exe asktgt /user:<USER> /rc4:<HASH>
Rubeus.exe s4u /impersonateuser:Administrator /msdsspn:cifs/<DC> /ptt
```

## Enumeración

- Credenciales iniciales de una cuenta de dominio sin privilegios.
- ACL y grupos que permiten modificar cuentas y equipos.
- 7-Zip instalado y contexto de shell de Windows modificable.

## Acceso inicial

Con la cuenta inicial se enumera AD y se identifican permisos de escritura sobre objetos. Se añade un SPN a una cuenta de equipo y se usa Timeroasting para obtener materiales que se crackean fuera de línea.

## Escalada de privilegios

Se secuestra la extensión de shell de 7-Zip en el perfil de un usuario con más privilegios y se obtiene ejecución en su contexto. Desde ahí se configura RBCD contra el DC y se solicita un ticket de servicio para administrar el dominio.

## Evidencia

- Enumeración de ACL y SPN escribible.
- Hashes de Timeroasting crackeados.
- RBCD configurado y ticket de administrador.

## Lecciones aprendidas

- Assume breach exige enumerar permisos, no solo servicios.
- Los SPN de cuentas de equipo son material sensible.
- Las extensiones de shell de aplicaciones de escritorio son persistencia y movimiento lateral.

## Mitigación y detección

- Auditar ACL y eliminar escrituras innecesarias sobre equipos.
- Monitorizar cambios de SPN y Timeroasting.
- Restringir extensiones de shell y aplicar LAPS/Protected Users.

## Referencias

- [0xdf — RustyKey](https://0xdf.gitlab.io/2025/11/08/htb-rustykey.html)
- [Timeroasting — Secura](https://www.secura.com/blog/timeroasting)
- [Hack The Box — RustyKey](https://app.hackthebox.com/machines/rustykey)
