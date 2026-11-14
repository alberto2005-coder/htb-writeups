---
topic: PIN del depurador de Flask
tags: [web, flask, werkzeug, debug, rce]
---

# PIN del depurador de Flask

[🌐 English](flask-debug-pin.en.md) | **Español**

## Concepto

Werkzeug protege la consola interactiva con un PIN derivado de datos del host: nombre de usuario, `machine-id`, MAC, ruta del módulo y nombre del proceso. Si el depurador está expuesto, el PIN se puede calcular o filtrar y la consola se convierte en ejecución remota.

## Cuándo aplica

- Flask con `debug=True` o `use_debugger=True`.
- La consola Werkzeug es accesible desde la red.
- Se puede leer `/etc/machine-id`, `/proc/self/cgroup` o el código de la app.

## Procedimiento

1. Provocar una excepción para abrir `/console`.
2. Reunir `username`, `modname`, `getattr(app, "__name__")`, `getattr(app, "__file__")`, MAC y `machine-id`.
3. Calcular el PIN con el algoritmo de `werkzeug.debug`.
4. Introducir el PIN y ejecutar comandos en el frame.

```python
import hashlib
from itertools import chain

# Completar con los valores del host
probably_public_bits = [username, modname, app_name, modfile]
private_bits = [str(machine_id), str(mac)]
```

## Variantes

- PIN filtrado por un LFI o un error que muestra el entorno.
- Consola accesible solo por localhost y túnel SSH.
- `debug=True` en un contenedor con `machine-id` predecible.

## Limitaciones

- El PIN cambia si cambian usuario, ruta o MAC.
- El depurador puede estar deshabilitado o filtrado.
- La consola no siempre ejecuta como root.

## Mitigación

- Nunca activar debug en producción.
- Bloquear `/console` en el proxy.
- Ejecutar la app con un usuario sin privilegios.

## Detección

- Respuestas 500 con traza de Werkzeug.
- Peticiones a `/console` y `__debugger__`.
- Procesos hijos inusuales del servidor web.

## Referencias

- <https://werkzeug.palletsprojects.com/en/stable/debug/>
- <https://flask.palletsprojects.com/en/stable/debugging/>
- <https://attack.mitre.org/techniques/T1190/>
