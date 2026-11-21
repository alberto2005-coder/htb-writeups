---
topic: Havoc C2 — SSRF y RCE encadenados (CVE-2024-41570)
tags: [web, havoc, c2, ssrf, websocket, cve-2024-41570, backfire]
---

# Havoc C2 — SSRF y RCE encadenados (CVE-2024-41570)

[🌐 English](havoc-ssrf-rce.en.md) | **Español**

## Concepto

Havoc 2 0.7 acepta comandos de los demonios (agentes) sin comprobar que el `RequestID` corresponda a una tarea emitida por el team server. Los comandos `COMMAND_SOCKET` y `COMMAND_PIVOT` están exentos de esa comprobación porque se usan para túneles. Un atacante puede registrar un agente falso y abrir un socket contra el puerto de administración interno; sobre ese socket habla WebSocket y alcanza el RCE autenticado de Havoc. En Backfire, la cadena SSRF→WebSocket→RCE dio shell como `ilya`.

## Cuándo aplica

- Havoc 2 0.7 expuesto, con el panel de administración en localhost o detrás de un proxy.
- El listener acepta callbacks de agentes desde la red del atacante.
- Existe una vía para enviar tráfico al puerto interno (SSRF, túnel, pivot).
- La configuración de Havoc se ha filtrado o se puede reconstruir.

## Procedimiento

1. Identificar el listener y el panel de administración de Havoc.
2. Registrar un agente falso con el comando `DEMON_INITIALIZE`.
3. Enviar `COMMAND_SOCKET` o `COMMAND_PIVOT` para abrir el túnel.
4. Hablar WebSocket contra el puerto de administración interno.
5. Usar el RCE autenticado para ejecutar comandos.
6. En Backfire, continuar con HardHatC2 y `iptables-save`.

## Comandos

```text
POST /<listener>  → agente con comando 99 (DEMON_INITIALIZE)
COMMAND_SOCKET    → socket sin RequestID
COMMAND_PIVOT     → túnel sin RequestID
```

```bash
# Túnel local hacia el panel interno
ssh -L 40056:127.0.0.1:40056 <USER>@<HOST>
```

## Variantes

- Reutilizar un agente ya registrado para abrir el socket.
- Encadenar el SSRF con un proxy inverso mal configurado.
- Aprovechar el pivot para alcanzar otros servicios internos.
- Combinar con la fuga de configuración para obtener claves y listeners.
- Usar el mismo patrón en otras versiones de Havoc si el código no cambió.

## Limitaciones

- La versión corregida valida el `RequestID` también para socket y pivot.
- Hace falta conocer el protocolo y la clave del listener.
- El panel interno puede estar en otro puerto o requerir TLS.
- La cadena depende de que el agente falso pueda registrarse.
- Las acciones quedan en los logs del team server.

## Mitigación

- Actualizar Havoc a una versión corregida.
- No exponer el panel de administración; separarlo del listener.
- Requerir autenticación y validar el `RequestID` en todos los comandos.
- Segmentar la red del C2 y limitar los callbacks.
- Rotar claves y revisar la configuración expuesta.

## Detección

- Agentes registrados desde IPs no habituales.
- Comandos `COMMAND_SOCKET` o `COMMAND_PIVOT` sin tarea previa.
- Conexiones del team server hacia su propio panel interno.
- WebSocket inesperados en el puerto de administración.
- Configuración de Havoc accesible desde servidores de archivos.

## Referencias

- [NVD — CVE-2024-41570](https://nvd.nist.gov/vuln/detail/CVE-2024-41570)
- [0xdf — Backfire](https://0xdf.gitlab.io/2025/06/07/htb-backfire.html)
- [Havoc — Documentación](https://havocframework.com/docs/welcome)
- [Ficha Backfire](../../machines/linux/backfire/README.md)
