---
topic: Bypass de filtros SSRF con redirecciones
tags: [web, ssrf, redirects, allowlist, bypass]
---

# Bypass de filtros SSRF con redirecciones

[🌐 English](ssrf-redirect-bypass.en.md) | **Español**

## Concepto

Un SSRF se produce cuando el servidor obtiene una URL controlada por el usuario. Si el filtro valida la URL inicial pero el cliente HTTP sigue redirecciones, un dominio externo puede responder `302` hacia un destino interno y saltar la comprobación.

## Cuándo aplica

- La aplicación permite introducir una URL y devuelve el contenido.
- El filtro bloquea `localhost`, `127.0.0.1` o nombres internos.
- El cliente sigue redirecciones automáticamente.

## Procedimiento

1. Confirmar que el servidor obtiene la URL y muestra la respuesta.
2. Alojar un endpoint que redirija al host o vhost interno.
3. Enviar la URL externa al parámetro vulnerable.
4. Usar el SSRF para leer archivos, metadatos o paneles internos.

```python
from flask import Flask, redirect
app = Flask(__name__)
@app.route("/")
def go():
    return redirect("http://admin.internal/")
app.run(host="0.0.0.0", port=80)
```

```bash
curl --data-urlencode 'url=http://<ATTACKER>/' http://<IP>/fetch
```

## Variantes

- Redirigir a `http://127.0.0.1:8080` o a un vhost interno.
- Encadenar varios redirects para evadir listas negras.
- Usar un dominio que resuelva a una IP interna.

## Limitaciones

- El cliente debe seguir redirecciones.
- El destino interno debe ser alcanzable desde el servidor.
- Algunos clientes bloquean cambios de esquema o de host.

## Mitigación y detección

- Validar el destino final tras resolver DNS y seguir redirects.
- Usar una allowlist estricta de esquemas, hosts y puertos.
- Bloquear rangos privados y metadatos en el cliente.

## Referencias

- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
- <https://attack.mitre.org/techniques/T1190/>
