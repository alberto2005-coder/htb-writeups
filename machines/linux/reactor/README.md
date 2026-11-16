---
machine: Reactor
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, nextjs, react2shell, cve-2025-55182, sqlite, node-inspector, privesc]
---

# Reactor — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web es NextJS 15.0.3 con React 19 RC y es vulnerable a React2Shell (CVE-2025-55182): un payload multipart en una Server Action permite deserializar datos y ejecutar código como `node`. La base SQLite de la aplicación contiene hashes MD5; el de `engineer` se crackea y se reutiliza para su cuenta. Un monitor de uptime corre como root con el inspector de Node en localhost:9229; un túnel SSH y el protocolo DevTools permiten ejecutar código en ese proceso y llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,3000 <IP>
```

- `22` OpenSSH 9.6 y `3000` NextJS.
- Cabeceras `x-nextjs-cache`, `x-nextjs-prerender` y `X-Powered-By: Next.js`.
- La aplicación es un panel de monitorización de reactores.

## Enumeración

Se descargan los chunks JS y se buscan versiones. NextJS es 15.0.3 y React 19.0.0-rc; la combinación es vulnerable a CVE-2025-55182. Se identifica una Server Action y se construye un cuerpo multipart con la cabecera `Next-Action`.

## Foothold

El payload de React2Shell deserializa un objeto con una cadena de prototipos que alcanza `child_process.execSync`. Se envía con `curl` y se obtiene ejecución como `node`; una reverse shell o un comando con base64 estabiliza el acceso.

```bash
# React2Shell
curl -X POST http://<IP>:3000/ -H 'Next-Action: <ACTION>' \
  -H 'Content-Type: multipart/form-data; boundary=----R2S' --data-binary @r2s-body.txt
# inspector root
ssh -L 9229:localhost:9229 engineer@<IP>
node inspect 127.0.0.1:9229```

## Movimiento lateral

`/opt/reactor-app/reactor.db` contiene la tabla `users` con hashes MD5. El de `engineer` se crackea y funciona tanto en la aplicación como en `su engineer` y SSH.

## Escalada de privilegios

`ps` muestra un monitor de uptime como root con `node --inspect=127.0.0.1:9229`. Se reabre SSH con `-L 9229:localhost:9229`, se conecta el inspector y se evalúa código en el proceso root; por ejemplo, copiar bash y darle SUID o escribir una clave en `/root/.ssh`.

## Evidencia

- Versiones NextJS/React vulnerables.
- Payload RSC y shell `node`.
- SQLite con hash de `engineer`.
- Inspector Node en localhost como root.

## Lecciones aprendidas

- Las versiones de frameworks se filtran en los chunks y cabeceras.
- RSC procesa datos del cliente y debe tratarse como no confiable.
- Los hashes MD5 de aplicaciones se reutilizan en cuentas del sistema.
- Un inspector de Node expuesto en localhost es ejecución root si se puede tunelizar.

## Mitigación y detección

- Actualizar React/NextJS a versiones corregidas.
- Validar y firmar payloads de Server Actions.
- Usar Argon2/bcrypt y contraseñas distintas por cuenta.
- No ejecutar monitores con `--inspect` como root; restringir 9229.

## Referencias

- [0xdf — Reactor](https://0xdf.gitlab.io/2026/10/03/htb-reactor.html)
- [IppSec — Reactor](https://www.youtube.com/watch?v=-mBxWU9vrJQ)
- [Hack The Box — Reactor](https://app.hackthebox.com/machines/reactor)
