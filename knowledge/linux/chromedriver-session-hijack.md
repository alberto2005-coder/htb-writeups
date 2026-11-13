---
topic: chromedriver session hijack
tags: [linux, chromedriver, froxlor, session-hijack, devtools, reload-cmd]
---

# chromedriver session hijack

[🌐 English](chromedriver-session-hijack.en.md) | **Español**

## Concepto

Un `chromedriver` local sin autenticación expone el puerto de DevTools y permite controlar el navegador de otro usuario. Si ese navegador tiene una sesión activa en un panel administrativo como Froxlor, el atacante puede robar la cookie y usar funciones privilegiadas como `reload_cmd` para ejecutar comandos.

## Cuándo aplica

- `chromedriver` escuchando en localhost.
- Navegador con sesión administrativa abierta.
- Panel Froxlor u otro con acciones de sistema.
- Capacidad de acceder al puerto desde la máquina.

## Procedimiento

1. Enumerar procesos y puertos locales.
2. Identificar `chromedriver` y su sesión.
3. Consultar `/json` para obtener el `webSocketDebuggerUrl`.
4. Robar cookies o ejecutar JavaScript en la pestaña.
5. Usar la sesión para invocar `reload_cmd` o una acción equivalente.

```bash
ps aux | grep -i chromedriver
curl -s http://127.0.0.1:9515/json
curl -s http://127.0.0.1:9515/json/version
```

## Variantes

- DevTools en el puerto 9222.
- Secuestro de una sesión de Froxlor con `reload_cmd`.
- Exfiltración de cookies y tokens CSRF.
- Uso de `Page.navigate` para acciones administrativas.

## Limitaciones

- El puerto debe ser accesible.
- La sesión debe estar autenticada y activa.
- El panel debe permitir la acción privilegiada.
- La cookie puede estar ligada a IP o expirar.

## Mitigación y detección

- No exponer `chromedriver` sin autenticación.
- Cerrar sesiones y navegadores tras tareas automatizadas.
- Restringir `reload_cmd` y validar la entrada.
- Auditar accesos a DevTools y acciones administrativas inusuales.

## Referencias

- <https://chromedevtools.github.io/devtools-protocol/>
- <https://froxlor.org/>
- <https://attack.mitre.org/techniques/T1185/>
