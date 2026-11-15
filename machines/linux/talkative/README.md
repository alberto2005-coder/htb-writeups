---
machine: Talkative
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, jamovi, rocket.chat, docker, capabilities, dac-read-search]
---

# Talkative — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La instancia de jamovi permite ejecutar R en el servidor y da acceso a un contenedor. El pivote entre contenedores lleva al host; un contenedor de Rocket.Chat con `CAP_DAC_READ_SEARCH` permite leer y escribir archivos fuera de su árbol y llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,3000 <IP>
curl -s http://talkative.htb/ | head
# Ejecución de R en jamovi
curl -s -X POST http://talkative.htb/run -d 'code=system("id")'
# Dentro del contenedor
capsh --print
mount | grep -E "host|docker"
cat /proc/1/root/etc/shadow 2>/dev/null
```

## Enumeración

- Jamovi accesible desde la web y ejecución de scripts R.
- Rocket.Chat en un contenedor con capacidades ampliadas.
- Montajes y sockets que conectan los contenedores con el host.

## Acceso inicial

El editor de jamovi acepta código R; se ejecuta un comando y se obtiene una shell en el contenedor. Desde ahí se enumeran redes, variables y montajes para localizar el siguiente salto.

## Escalada de privilegios

El contenedor de Rocket.Chat tiene `CAP_DAC_READ_SEARCH`, que ignora los permisos de lectura de archivos. Se leen claves y configuraciones del host, se escribe una tarea o un archivo privilegiado y se ejecuta como root.

## Evidencia

- Ejecución de R en jamovi y shell en el contenedor.
- `capsh --print` con `cap_dac_read_search`.
- Lectura de archivos del host y shell de root.

## Lecciones aprendidas

- Los editores de análisis con ejecución de scripts son RCE por diseño.
- Las capabilities amplían el impacto de un contenedor comprometido.
- Los montajes del host convierten una lectura en escritura privilegiada.

## Mitigación y detección

- Aislar jamovi y no permitir scripts arbitrarios.
- Quitar `CAP_DAC_READ_SEARCH` y montar secretos como solo lectura.
- Segmentar contenedores y aplicar seccomp/AppArmor.

## Referencias

- [0xdf — Talkative](https://0xdf.gitlab.io/2022/08/27/htb-talkative.html)
- [Docker — Capabilities](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)
- [Hack The Box — Talkative](https://app.hackthebox.com/machines/talkative)
