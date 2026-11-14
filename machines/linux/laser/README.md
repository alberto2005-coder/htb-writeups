---
machine: Laser
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, printer, pjl, grpc, solr, ssh, docker]
---

# Laser — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Dos puertos poco habituales: JetDirect (9100) y un servicio gRPC (9000). Del printer se extrae un trabajo cifrado y la clave en memoria, que revela la especificación de Feed Engine. Se escribe un cliente gRPC que hace SSRF contra Apache Solr en localhost y permite RCE como `solr`. En el host, `pspy` muestra a root usando `sshpass` hacia un contenedor; se intercepta esa conexión y se controla `clear.sh` para obtener una bash SUID en el host.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,9000,9100 <IP>
python3 /opt/PRET/pret.py <IP> pjl
```

## Enumeración

- 9100 responde a PJL y se identifica como una impresora LaserCorp.
- El trabajo en cola está cifrado; `nvram dump` filtra la clave AES.
- El PDF descifrado describe Feed Engine v1.0, gRPC y el puerto 9000.

## Acceso inicial

Se descifra el trabajo con AES-CBC (IV en los bytes 8-23) y se lee el PDF, que define el servicio `Print.Feed`. Se genera el cliente con `grpc_tools.protoc` y se envía una URL de feed apuntando a Solr en `127.0.0.1:8983`. Al habilitar el cargador de plantillas Velocity se ejecuta código y se obtiene una shell como `solr`.

## Escalada de privilegios

`pspy` revela que root usa `sshpass` para copiar y ejecutar `/tmp/clear.sh` en el contenedor `172.18.0.2`. Se entra al contenedor con esa contraseña, se sustituye sshd por `socat` hacia el host y se prepara un `clear.sh` no escribible; el `scp` falla, pero el `ssh` posterior ejecuta el contenido controlado y crea una bash SUID en el host.

## Evidencia

- Trabajo de impresión descifrado y PDF con el protocolo.
- Petición SSRF a Solr y shell como `solr`.
- `clear.sh` ejecutado por root y bash SUID en el host.

## Lecciones aprendidas

- Las impresoras y servicios industriales filtran memoria y credenciales.
- gRPC y Protocol Buffers se pueden invertir a partir de documentación filtrada.
- Un contenedor con la clave de root no es una frontera si root confía en él.

## Mitigación y detección

- Aislar impresoras y deshabilitar PJL/NVRAM sin autenticación.
- No exponer Solr ni habilitar Velocity para usuarios no confiables.
- Evitar `sshpass`, claves compartidas y scripts en `/tmp` ejecutados por root.

## Referencias

- [0xdf — Laser](https://0xdf.gitlab.io/2020/12/19/htb-laser.html)
- [IppSec — Laser](https://www.youtube.com/watch?v=vD3jSJlc0ro)
- [Hack The Box — Laser](https://app.hackthebox.com/machines/laser)
