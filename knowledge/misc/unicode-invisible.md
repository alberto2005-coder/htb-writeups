---
title: Caracteres invisibles y puertas traseras Unicode
tags: [misc, unicode, javascript, backdoor, code-review]
---

# Caracteres invisibles y puertas traseras Unicode

[🇬🇧 English](unicode-invisible.en.md) | **Español**

## 1. Cuándo mirar aquí

Un código «normal» se comporta distinto de lo que parece: una variable que no está, una coma final extraña, una comparación que siempre falla. Los caracteres invisibles son una técnica de ofuscación barata y difícil de ver en un editor.

## 2. Los que aparecen en retos

| Carácter | Code point | Aspecto | Uso típico |
|---|---|---|---|
| HANGUL FILLER | `U+3164` | como un espacio | identificador válido en JS |
| ZERO WIDTH SPACE | `U+200B` | nada | separar tokens o marcar |
| ZERO WIDTH JOINER | `U+200D` | nada | unir emojis; también ofusca |
| WORD JOINER | `U+2060` | nada | evitar cortes |
| RIGHT-TO-LEFT OVERRIDE | `U+202E` | invierte el orden visual | ocultar extensiones |
| Homoglifos cirílicos | `U+0430`… | igual que `a`, `e`, `o` | suplantar identificadores |

En JavaScript, `U+3164` pertenece a la categoría *Letter, other* y es un identificador legal. Por eso `const { choice,ㅤ} = req.body;` declara una segunda variable que nadie ve.

## 3. Detección

`cat -A` los convierte en bytes escapados y no revela el code point; `xxd` sí:

```bash
grep -nP "[^\x00-\x7F]" app.js
python3 -c "import unicodedata,sys;print([unicodedata.name(c) for c in open('app.js').read() if ord(c)>127])"
```

Editores: VS Code resalta por defecto caracteres invisibles y confundibles desde la 1.63 (U+3164 incluido); vim no. Un linter con regla `no-irregular-whitespace` o `non-ascii` ayuda en CI.

## 4. Caso típico

Un endpoint que solo acepta índices de una lista fija y, sin embargo, ejecuta un comando elegido por el cliente. El array tiene una coma final que parece estilo y en realidad añade una variable leída del cuerpo de la petición: el índice 6 pasa el control de rango porque `commands.length` ya incluye el elemento inyectado.

## 5. Bidi y extensiones

`U+202E` invierte la representación: `informe\u202Efdp.exe` se ve como `informeexe.pdf`. En nombres de fichero, combinarlo con homoglifos permite engañar a un usuario y, a veces, a una comprobación de extensión. Normalizar a NFC/NFKC no elimina el bidi: hay que rechazar categorías de control.

## 6. Mitigación

- Rechazar en validación cualquier carácter fuera de un conjunto permitido (ASCII imprimible para claves e identificadores).
- Esquemas estrictos de cuerpo: `choice` numérico y ninguna clave extra.
- No construir listas de comandos con datos de la petición.
- En revisión de código, buscar `U+3164`, `U+200B` y bidi; un diff que «no cambia nada» puede estar añadiendo una variable.

## 7. Detección en producción

- WAF/validación con lista blanca de caracteres en parámetros y nombres de campo.
- Alertas sobre claves de formulario no ASCII o con espacios invisibles.
- En logs, comparar el número de claves recibidas con las esperadas.

Referencias: Unicode TR39 (confusables), el artículo de Certitude sobre la puerta trasera invisible y la documentación de identificadores de ECMAScript.
