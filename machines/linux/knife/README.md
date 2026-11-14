---
machine: Knife
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, php, backdoor, chef, sudo]
---

# Knife — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web anuncia PHP 8.1.0-dev, la versión con la puerta trasera de `User-Agentt`. Se envía el encabezado malicioso y se obtiene una shell como `james`; `sudo knife` permite ejecutar Ruby como root y cerrar la máquina.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
curl -s http://<IP>/ | head
```

## Enumeración

- La respuesta incluye `X-Powered-By: PHP/8.1.0-dev`.
- No hay rutas ni formularios relevantes; la web es una sola página.
- `james` puede ejecutar `/usr/bin/knife` con sudo sin contraseña.

## Acceso inicial

La versión 8.1.0-dev incluye una puerta trasera que evalúa el valor de `User-Agentt` cuando empieza por `zerodium`. Se envía una llamada a `system` con una reverse shell y se obtiene ejecución como `james`.

## Escalada de privilegios

`sudo -l` muestra `(root) NOPASSWD: /usr/bin/knife`. Knife es la CLI de Chef y su subcomando `exec` evalúa Ruby; `sudo knife exec -E "exec '/bin/bash'"` abre una shell de root. Como alternativa, `knife data bag create` abre Vim y `:!/bin/bash` escapa.

## Evidencia

- Cabecera `X-Powered-By` con 8.1.0-dev.
- Petición con `User-Agentt` y shell como `james`.
- `sudo knife exec` y `id` como root.

## Lecciones aprendidas

- La versión exacta de un servicio puede ser una vulnerabilidad en sí misma.
- Las CLI de automatización con `exec` son equivalentes a sudo completo.
- Revisar `sudo -l` sigue siendo prioritario.

## Mitigación y detección

- No ejecutar builds de desarrollo en producción.
- Restringir `knife` y eliminar `exec` de las reglas sudo.
- Monitorizar encabezados HTTP anómalos y procesos hijos de PHP.

## Referencias

- [0xdf — Knife](https://0xdf.gitlab.io/2021/08/28/htb-knife.html)
- [IppSec — Knife](https://www.youtube.com/watch?v=93JnRTF5sQM)
- [Hack The Box — Knife](https://app.hackthebox.com/machines/knife)
