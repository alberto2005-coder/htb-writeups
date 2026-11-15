---
machine: BlockBlock
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, xss, ethereum, json-rpc, pacman, path-hijack]
---

# BlockBlock — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un XSS en el chat y un endpoint que filtra el token permiten entrar como administrador. La aplicación consulta una blockchain Ethereum; los datos de un bloque contienen credenciales SSH. `forge` con PATH hijacking y `pacman` cierran la escalada.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8545 <IP>
ffuf -u http://blockblock.htb/FUZZ -w /usr/share/wordlists/dirb/common.txt
# XSS en el chat y robo de token
curl -s -X POST http://blockblock.htb/api/chat -d '{"message":"<img src=x onerror=fetch('/api/token')>"}'
# Ethereum JSON-RPC
curl -s -X POST http://blockblock.htb:8545 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",true],"id":1}'
forge --help
pacman -Qo /usr/bin/forge
```

## Enumeración

- Aplicación de chat con XSS y un endpoint de token.
- Nodo Ethereum JSON-RPC con bloques legibles.
- Usuario con `forge` y permisos de `pacman`.

## Acceso inicial

El XSS ejecuta en el navegador del bot y roba el token de administrador. Con el token se accede al panel y se consulta el JSON-RPC; un bloque contiene un mensaje con credenciales SSH.

## Escalada de privilegios

`forge` se ejecuta en un contexto con más privilegios y permite PATH hijacking. Después, un hook de `pacman` o una regla de instalación ejecutada como root permite crear un paquete malicioso y obtener root.

## Evidencia

- Callback XSS con el token.
- Consulta `eth_getBlockByNumber` con datos en hex.
- `forge` con PATH manipulado y `pacman` ejecutando el hook.

## Lecciones aprendidas

- La blockchain es un canal de datos público y permanente.
- Un token en el cliente puede convertirse en acceso administrativo.
- Los gestores de paquetes con hooks ejecutan código privilegiado.

## Mitigación y detección

- Sanear el chat y no exponer tokens en endpoints.
- No usar la blockchain para secretos.
- Revisar hooks de `pacman` y rutas de `forge`.

## Referencias

- [0xdf — BlockBlock](https://0xdf.gitlab.io/2025/03/29/htb-blockblock.html)
- [Ethereum — JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [Hack The Box — BlockBlock](https://app.hackthebox.com/machines/blockblock)
