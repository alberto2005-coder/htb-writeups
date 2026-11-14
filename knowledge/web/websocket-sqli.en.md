---
topic: SQLi sobre WebSocket
tags: [web, websocket, sqli, sqlite, api]
---

# SQLi sobre WebSocket

[🌐 Español](websocket-sqli.md) | **English**

## Concept

A WebSocket carries JSON or text that the server uses to build SQL queries. Traditional HTTP tools do not see it, but a WebSocket client or proxy can replay the message and exploit the injection.

## When it applies

- An application sends commands over `ws://` or `wss://`.
- The server concatenates JSON fields into SQLite/MySQL.
- Burp or sqlmap do not detect the endpoint on their own.

## Procedure

1. Capture the handshake and messages with DevTools or Burp.
2. Replay a valid message with a Python client.
3. Alter a field with `'`, `UNION` or `OR`.
4. Match columns and types.
5. Extract data and test credential reuse.

```python
import websocket, json
ws = websocket.create_connection("ws://<HOST>:<PORT>/version")
ws.send(json.dumps({"version": "' UNION SELECT ... --"}))
print(ws.recv())
```

## Variants

- Injection in an unquoted numeric field.
- SQLite `UNION SELECT` with four columns.
- WebSocket proxy to drive sqlmap.

## Limitations

- The server may validate the JSON schema.
- The connection may require a token.
- The engine may not allow `UNION`.

## Mitigation

- Parameterized queries and type validation.
- Per-message authentication and authorization.
- Rate limits and close anomalous connections.

## Detection

- Messages containing quotes, `UNION` or SQL comments.
- SQLite errors in WebSocket logs.
- Repeated connections from the same client.

## References

- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://datatracker.ietf.org/doc/html/rfc6455>
- <https://attack.mitre.org/techniques/T1190/>
