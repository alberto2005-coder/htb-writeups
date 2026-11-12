---
challenge: Spiky Tamagotchi
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, javascript, code-injection, authentication-bypass]
---

# Spiky Tamagotchi — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La aplicación evalúa JavaScript con datos del usuario para “alimentar” a la mascota. Una inyección de código permite saltarse la autenticación y ejecutar comandos en el servidor.

## Enunciado y superficie

- Web, Easy, retirado.
- Interfaz de mascota virtual con acciones.
- No hay credenciales iniciales.

```bash
curl -i http://<HOST>/
```

## Reconocimiento

Se revisan las peticiones y el código JS. Las acciones envían un nombre/expresión que el backend evalúa.

```bash
curl -X POST http://<HOST>/api/feed -H 'Content-Type: application/json' -d '{"name":"test"}'
```

## Análisis

1. Se confirma la evaluación de expresiones.
2. Se inyecta una expresión que cambia el estado de autenticación.
3. Se accede al panel de administración.
4. Se ejecuta un comando o se lee el archivo de flag.
5. Se redacta la salida.

```javascript
1; return process.mainModule.require('child_process').execSync('id')
```

## Explicación del fallo

El servidor usa `eval`/`Function` con entrada no confiable. La lógica de autenticación vive en el mismo contexto, por lo que la inyección puede modificarla.

## Reproducción local

1. Montar la app.
2. Probar una expresión aritmética.
3. Inyectar código.
4. Verificar el bypass.
5. Corregir y comparar.

## Evidencia

- Petición con la expresión.
- Bypass de autenticación.
- Comando y flag redactada.

## Lecciones aprendidas

- `eval` con entrada de usuario es RCE.
- La autenticación no debe compartir contexto con el código evaluado.
- JavaScript del servidor tiene acceso a `process`.
- La validación por lista negra es frágil.

## Mitigación y detección

- Eliminar `eval`/`Function` con datos de usuario.
- Usar parsers y allowlists.
- Aislar la lógica de autenticación.
- Monitorizar procesos hijos del servidor Node.

## Referencias

- <https://www.hackthebox.com/challenges/spiky-tamagotchi>
- <https://owasp.org/www-community/attacks/Code_Injection>
- <https://nodejs.org/api/child_process.html>
