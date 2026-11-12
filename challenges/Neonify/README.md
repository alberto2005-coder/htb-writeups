---
challenge: Neonify
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ssti, crlf, regex-bypass, ruby]
---

# Neonify — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app “neoniza” texto con una plantilla y filtra palabras clave con una regex débil. Un salto de línea/CRLF y una expresión SSTI permiten ejecutar código y leer la flag.

## Enunciado y superficie

- Web, Easy, retirado.
- Formulario que transforma texto.
- Filtro por regex.

```bash
curl -i http://<HOST>/
```

## Reconocimiento

Se prueba una expresión aritmética y se observa si se evalúa. Se revisan los caracteres bloqueados y el motor de plantillas (Ruby/ERB).

```text
<%= 7*7 %>
```

## Análisis

1. Se identifica el filtro y se busca un bypass con `%0a`, mayúsculas o concatenación.
2. Se confirma SSTI.
3. Se ejecuta un comando del sistema.
4. Se lee la flag.
5. Se redacta la salida.

```text
<%= system('cat /flag*') %>
```

## Explicación del fallo

La regex no cubre saltos de línea ni variantes de sintaxis, y la entrada se evalúa en la plantilla. El filtro es una lista negra incompleta.

## Reproducción local

1. Montar la app con ERB.
2. Probar la expresión.
3. Aplicar el bypass CRLF.
4. Ejecutar `id`.
5. Corregir el filtro y comparar.

## Evidencia

- Petición con bypass.
- Salida de comandos.
- Flag redactada.

## Lecciones aprendidas

- Las regex de lista negra son frágiles.
- CRLF puede romper la validación.
- ERB evalúa código Ruby.
- El contexto de la plantilla importa.

## Mitigación y detección

- No evaluar entrada como plantilla.
- Usar renderizado seguro y escape.
- Allowlist de caracteres.
- Monitorizar procesos hijos del servidor.

## Referencias

- <https://www.hackthebox.com/challenges/neonify>
- <https://owasp.org/www-community/attacks/Server_Side_Template_Injection>
- <https://www.ruby-lang.org/en/documentation/