---
challenge: Trapped Source
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, client-side, source-code, pin, information-disclosure]
---

# Trapped Source — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La página pide un PIN, pero el código JavaScript del cliente incluye el valor esperado en claro. No hay validación en el servidor que proteja el secreto: basta con abrir el código fuente, leer el PIN y enviarlo.

## Enunciado y superficie

- Web, Very Easy, retirado.
- Se entrega una URL con un formulario de PIN.
- El objetivo es acceder a la pantalla que muestra la flag.

```bash
curl -s http://<IP>:<PORT>/ | head -n 40
```

## Reconocimiento

- La respuesta es HTML estático con un formulario y un script.
- No hay cabeceras ni rutas adicionales relevantes.
- El campo acepta cuatro dígitos y valida en el navegador.

```bash
curl -s http://<IP>:<PORT>/ | grep -iE 'pin|script|input'
```

## Análisis del código

El script compara la entrada con una constante. La comparación y el valor están incluidos en el bundle, por lo que cualquiera puede leerlos con el inspector o con `curl`.

```javascript
const expected = "<PIN>";
if (value === expected) { showFlag(); }
```

No existe una llamada al servidor que valide el PIN antes de revelar el contenido; la protección es puramente visual.

## Explicación del fallo

La aplicación trata un secreto de cliente como si fuera una barrera de seguridad. El navegador debe conocer el valor para compararlo, así que el valor es accesible. La comprobación se puede omitir modificando el estado local o enviando el PIN correcto.

## Reproducción local

```bash
# Guardar la página y abrirla en un navegador local.
curl -s http://<IP>:<PORT>/ -o trapped.html
```

- Abrir `trapped.html` y ver el código fuente.
- Buscar la constante del PIN.
- Introducirla en el formulario.

## Explotación

1. Ver el código fuente con `Ctrl-U` o `curl`.
2. Localizar la constante que se compara con el input.
3. Enviar el PIN.
4. La página muestra la flag; se redacta.

```bash
curl -s http://<IP>:<PORT>/ | grep -oE '[0-9]{4}' | head
```

## Evidencia

- Captura del código fuente con el PIN redactado.
- Formulario enviado y pantalla de éxito.
- Flag redactada.

## Lecciones aprendidas

- Un secreto en el cliente no es un secreto.
- La validación debe ocurrir en el servidor y el secreto no debe enviarse al navegador.
- El código fuente es parte de la superficie de ataque.

## Mitigaciones y detección

- Validar el PIN en el servidor con rate limiting y bloqueo.
- No incluir el valor esperado ni la flag en el bundle.
- Servir la flag solo tras una sesión autenticada y autorizada.
- Alertar de intentos repetidos y de descargas masivas del HTML.

## Referencias

- <https://www.hackthebox.com/challenges/Trapped%20Source>
- <https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure>
- <https://attack.mitre.org/techniques/T1213/>
