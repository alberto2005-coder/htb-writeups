---
topic: OAuth — CSRF por falta de state
tags: [web, oauth, csrf, state, account-linking]
---

# OAuth — CSRF por falta de state

[🌐 English](oauth-csrf-state.en.md) | **Español**

## Concepto

El parámetro `state` vincula la respuesta de autorización con la sesión que inició el flujo. Si no se valida, un atacante puede hacer que la víctima complete un flujo con el código del atacante y enlazar su cuenta, o al revés, tomar la cuenta de la víctima.

## Cuándo aplica

- El servidor OAuth no valida `state` o lo acepta vacío.
- La aplicación permite enlazar cuentas o iniciar sesión con el proveedor.
- El callback se puede predecir o reutilizar.

## Procedimiento

1. Iniciar el flujo y capturar el callback.
2. Comprobar si `state` se valida o cambia.
3. Forzar a la víctima a visitar la URL de autorización del atacante.
4. Usar la cuenta enlazada para acceder a la aplicación.

## Comandos

```bash
# Iniciar el flujo y observar state
curl -i "http://<HOST>/oauth/authorize?client_id=<ID>&redirect_uri=http://<HOST>/callback"
# Callback sin state
curl -i "http://<HOST>/oauth/callback?code=<CODE>"
# Enviar la URL al bot o a la víctima
```

## Variantes

- Login CSRF: la víctima inicia sesión con la cuenta del atacante.
- Account linking: se enlaza la cuenta del atacante a la víctima.
- Reutilizar un `state` fijo o predecible.

## Limitaciones

- Un `state` aleatorio y vinculado a la sesión bloquea el ataque.
- PKCE y SameSite reducen la superficie.
- El flujo puede requerir interacción del usuario.

## Mitigación

- Generar `state` aleatorio y validarlo contra la sesión.
- Usar PKCE y cookies `SameSite=Lax`.
- Pedir confirmación explícita al enlazar cuentas.

## Detección

- Callbacks sin `state` o con valores repetidos.
- Enlaces de autorización abiertos desde correos o chats.
- Enlazaciones de cuenta desde ubicaciones inusuales.

## Referencias

- [OAuth 2.0 — Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [PortSwigger — OAuth CSRF](https://portswigger.net/web-security/oauth)
- [0xdf — Oouch](https://0xdf.gitlab.io/2020/08/01/htb-oouch.html)
