---
title: ERB SSTI — saltar la regex con un salto de línea
tags: [web, ruby, erb, ssti, regex, rce]
---

# ERB SSTI — saltar la regex con un salto de línea

[🇬🇧 English](erb-ssti-newline.en.md) | **Español**

## Concepto

En Ruby, `^` y `$` anclan al inicio y final de **línea**, no de cadena. Una validación `params[:x] =~ /^[a-z]+$/` acepta `abc\n<%= ... %>` porque el salto de línea satisface `$` y el resto queda fuera de la comprobación. Si ese valor se interpola en una plantilla ERB, se ejecuta.

## Cuándo aplica

- La aplicación es Ruby/Sinatra/Rails y usa ERB.
- La entrada se valida con `^...$` y luego se concatena en `ERB.new(...).result(binding)`.
- Se permite un salto de línea en el parámetro.

## Procedimiento

1. Enviar un valor válido seguido de `%0a` y `<%= 7*7 %>`.
2. Comprobar si la respuesta devuelve `49`.
3. Sustituir por `system` o backticks para ejecutar.
4. Codificar la reverse shell si hay filtros.

```text
category1=Test%0a<%= 7*7 %>
category1=Test%0a<%= system("id") %>
```

```ruby
ERB.new("... #{params[:category1]} ...").result(binding)
```

## Variantes

- Usar `\n` real en un cuerpo JSON o `%0a` en formularios.
- Si `system` está bloqueado, `IO.popen`, backticks o `eval`.
- En Rails, `render inline:` con entrada del usuario tiene el mismo problema.

## Limitaciones

- La regex debe usar `^`/`$` y no `\A`/`\z`.
- El valor debe llegar a una plantilla ERB, no a una salida escapada.
- Los filtros de palabras pueden requerir concatenación.

## Mitigación y detección

- Validar con `\A...\z` y listas blancas.
- No construir plantillas con entrada; usar variables escapadas.
- Deshabilitar `ERB.new` sobre datos no confiables.
- Buscar `%0a`, `<%` y `%>` en parámetros y alertar.

## Referencias

- <https://ruby-doc.org/stdlib-3.3.0/libdoc/erb/rdoc/ERB.html>
- <https://portswigger.net/web-security/server-side-template-injection>
- <https://owasp.org/www-community/attacks/Code_Injection>
