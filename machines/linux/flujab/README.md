---
machine: FluJab
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, vhosts, sqli, ajenti, ssh, screen]
---

# FluJab — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La enumeración de vhosts y la manipulación de cookies exponen páginas de configuración. Una SQLi recupera datos enviados por correo, incluidas credenciales de Ajenti. Ajenti revela claves SSH débiles; se añade la IP al whitelist de TCP wrappers y se entra con la clave. La escalada escapa de `rbash` y explota `screen`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
ffuf -u http://flujab.htb -H "Host: FUZZ.flujab.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# Cookie de configuración
curl -s -b "role=admin" http://flujab.htb/config/
# SQLi
sqlmap --url "http://flujab.htb/search.php?q=test" --batch --dump
# Ajenti y clave débil
ssh -i debian_key <USER>@<IP>
# Escape y screen
vi
screen -version
screen -x root/root
```

## Enumeración

- Varios vhosts y una cookie que controla el contexto de configuración.
- Formulario con SQLi y correo interno con credenciales.
- Ajenti con claves SSH generadas por Debian débil (CVE-2008-0166).

## Acceso inicial

Se enumeran subdominios y se prueba a elevar privilegios en la cookie para acceder a páginas de administración. La SQLi devuelve el correo con credenciales de Ajenti; en Ajenti se descarga una clave SSH débil y se añade la IP atacante a `/etc/hosts.allow` desde el panel.

## Escalada de privilegios

La cuenta entra en `rbash`; se escapa con `vi`, `less` o una variable de entorno. La versión de `screen` es vulnerable y permite ejecutar comandos fuera de la sesión restringida, dando root.

## Evidencia

- Vhost y cookie manipulada con panel de configuración.
- Credenciales de Ajenti y clave SSH aceptada.
- Escape de rbash y exploit de screen.

## Lecciones aprendidas

- Las cookies de contexto deben validarse en servidor.
- Las claves SSH antiguas de Debian son recuperables.
- `rbash` no es una jaula si queda un editor o `screen` vulnerable.

## Mitigación y detección

- Firmar y validar cookies; no confiar en el rol del cliente.
- Regenerar claves SSH y restringir Ajenti.
- Actualizar screen y eliminar shells restringidas mal configuradas.

## Referencias

- [0xdf — FluJab](https://0xdf.gitlab.io/2019/06/15/htb-flujab.html)
- [Ajenti — Documentation](https://docs.ajenti.org/)
- [Hack The Box — FluJab](https://app.hackthebox.com/machines/flujab)
