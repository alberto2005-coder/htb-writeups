---
topic: SQLi sobre WebSocket
tags: [web, websocket, sqli, sqlite, api]
---

# SQLi sobre WebSocket

[🌐 English](websocket-sqli.en.md) | **Español**

## Concepto

Un WebSocket transporta JSON o texto que el servidor usa para construir consultas SQL. Las herramientas HTTP tradicionales no lo ven, pero un cliente WebSocket o un proxy permite reproducir el mensaje y explotar la inyección.

## Cuándo aplica

- Aplicación que envía comandos por `ws://` o `wss://`.
- El servidor concatena campos JSON en SQLite/MySQL.
- Burp o sqlmap no detectan el endpoint por sí solos.

## Procedimiento

1. Capturar el handshake y los mensajes con las DevTools o Burp.
2. Reproducir un mensaje válido con un cliente Python.
3. Alterar un campo con `'`, `UNION` o `OR`.
4. Ajustar columnas y tipos.
5. Extraer datos y probar reutilización de credenciales.

```python
import websocket, json
ws = websocket.create_connection("ws://<HOST>:<PORT>/version")
ws.send(json.dumps({"version": "' UNION SELECT ... --"}))
print(ws.recv())
```

## Variantes

- Inyección en un campo numérico sin comillas.
- SQLite con `UNION SELECT` de cuatro columnas.
- Proxy WebSocket para usar sqlmap.

## Limitaciones

- El servidor puede validar el esquema JSON.
- La conexión puede exigir un token.
- El motor puede no permitir `UNION`.

## Mitigación

- Consultas parametrizadas y validación de tipos.
- Autenticación y autorización por mensaje.
- Límites de tasa y cierre de conexiones anómalas.

## Detección

- Mensajes con comillas, `UNION` o comentarios SQL.
- Errores de SQLite en logs del WebSocket.
- Conexiones repetidas desde el mismo cliente.

## Referencias

- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://datatracker.ietf.org/doc/html/rfc6455>
- <https://attack.mitre.org/techniques/T1190/>
