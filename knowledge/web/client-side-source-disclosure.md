---
topic: Divulgación de código en el cliente
tags: [web, javascript, source-maps, secrets, information-disclosure]
---

# Divulgación de código en el cliente

[🌐 English](client-side-source-disclosure.en.md) | **Español**

## Concepto

El navegador necesita ejecutar JavaScript, por lo que el código y los datos embebidos son accesibles. Comentarios, bundles sin minificar, source maps, variables de configuración y constantes de validación pueden revelar rutas, claves, PINs o lógica interna.

## Cuándo aplica

- Aplicaciones SPA con bundles grandes.
- Archivos `.map` accesibles.
- Comentarios HTML con credenciales o rutas.
- Validaciones de PIN, cupones o roles en JavaScript.
- Variables `API_KEY`, `SECRET` o endpoints internos.

## Procedimiento

1. Ver el código fuente y la pestaña Network.
2. Buscar archivos `.js`, `.map` y `chunk`.
3. Revisar comentarios y cadenas con `grep`.
4. Formatear el bundle con `prettier` o la herramienta del navegador.
5. Probar rutas y valores descubiertos.

```bash
curl -s https://<HOST>/ | grep -oE 'src="[^"]+\.js[^"]*"'
curl -s https://<HOST>/static/app.js | grep -iE 'api|secret|token|pin|admin'
```

## Variantes

- Source map que reconstruye el árbol de fuentes.
- Secreto de API en el bundle.
- Lógica de validación de PIN o descuento.
- Ruta de administración oculta.
- Comentario con credenciales de prueba.

## Limitaciones

- Un secreto en el cliente no protege nada, pero puede ser de solo lectura.
- Los source maps pueden estar deshabilitados en producción.
- Los bundles ofuscados dificultan la lectura, no la impiden.
- Las claves restringidas por dominio reducen el impacto.

## Mitigación y detección

- No incluir secretos ni lógica de autorización en el cliente.
- Deshabilitar source maps en producción o restringirlos.
- Validar todo en el servidor.
- Alertar de descargas de `.map` y de acceso a rutas descubiertas.

## Referencias

- <https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure>
- <https://cwe.mitre.org/data/definitions/540.html>
- <https://attack.mitre.org/techniques/T1213/>
- <https://developer.chrome.com/docs/devtools/javascript/source-maps/>
