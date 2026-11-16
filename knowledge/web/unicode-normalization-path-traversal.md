---
topic: Unicode — normalización y path traversal
tags: [web, unicode, normalization, path-traversal, lfi, nfkc]
---

# Unicode — normalización y path traversal

[🌐 English](unicode-normalization-path-traversal.en.md) | **Español**

## Concepto

Un filtro que busca la cadena `../` antes de normalizar puede dejar pasar caracteres que, tras la normalización Unicode, se convierten en puntos. `U+2025` (dos puntos suspensivos horizontales, `‥`) se normaliza a `..` en NFKC. Si el sistema de archivos o el framework normaliza después del filtro, el traversal se ejecuta.

## Cuándo aplica

- La aplicación filtra `../` o `..\\` en la entrada.
- La cadena se normaliza (NFKC/NFKD) o se procesa con una API que lo hace.
- El parámetro se usa para construir una ruta de archivo.
- El lenguaje o el framework aplica normalización al abrir el recurso.

## Procedimiento

1. Confirmar el filtro y qué variantes bloquea.
2. Probar caracteres que se normalicen a `.` o `/`.
3. Construir la secuencia equivalente a `../`.
4. Leer un archivo conocido para validar.
5. Escalar a configuración, claves o código fuente.

## Comandos

```text
/display/?page=..%E2%80%A5/..%E2%80%A5/app.py
# U+2025 se normaliza a ".." en NFKC
```

```python
import unicodedata
print(unicodedata.normalize("NFKC", "\u2025"))  # ..
```

## Variantes

- `U+FF0E` (punto fullwidth) y `U+FF0F` (barra fullwidth).
- Normalización en el sistema de archivos (macOS, Windows).
- Doble normalización: una en el filtro y otra al abrir.

## Limitaciones

- El framework debe normalizar después del filtro.
- Algunos sistemas de archivos no normalizan.
- La ruta debe ser válida para el proceso.
- Los filtros posteriores pueden bloquear el resultado.

## Mitigación

- Normalizar a NFKC antes de validar.
- Resolver con `realpath` y comprobar el prefijo permitido.
- Usar listas blancas de páginas o identificadores.
- No construir rutas con entrada del usuario.

## Detección

- Parámetros con caracteres Unicode exóticos.
- Rutas que contienen `U+2025`, `U+FF0E` o sobrecodificaciones.
- Lecturas de `app.py`, `.env` o claves desde el servidor web.
- Errores de apertura de archivos con rutas normalizadas.

## Referencias

- [Unicode — UAX #15](https://unicode.org/reports/tr15/)
- [OWASP — Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [0xdf — Unicode](https://0xdf.gitlab.io/2022/05/07/htb-unicode.html)
