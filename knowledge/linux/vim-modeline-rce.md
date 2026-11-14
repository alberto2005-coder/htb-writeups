---
topic: Vim — ejecución mediante modeline
tags: [linux, vim, modeline, rce, editor]
---

# Vim — ejecución mediante modeline

[🌐 English](vim-modeline-rce.en.md) | **Español**

## Concepto

Vim puede aplicar opciones declaradas en las primeras o últimas líneas de un fichero (`modeline`). Si `modelineexpr` está activo, una expresión como `foldexpr` o `statusline` puede ejecutar comandos al abrir el fichero.

## Cuándo aplica

- Víctima que abre un fichero con Vim y `modeline` habilitado.
- `modelineexpr` o versiones antiguas vulnerables.
- Editores usados por root o por un servicio.

## Procedimiento

1. Comprobar `:set modeline?` y `:set modelineexpr?`.
2. Crear un fichero con un modeline malicioso.
3. Conseguir que la víctima lo abra con Vim.
4. Verificar la ejecución con un fichero de prueba.
5. Escalar si el editor se ejecuta como root.

## Comandos

```vim
" Modeline de prueba
vim: set foldmethod=expr foldexpr=system('id'):
```

## Variantes

- `statusline` con `%{system('id')}`.
- `errorformat` o `makeprg`.
- Abrir el fichero desde `git`, `less` o un editor integrado.

## Limitaciones

- `modeline` puede estar deshabilitado.
- `modelineexpr` solo existe en versiones recientes.
- El fichero debe abrirse con Vim, no con `cat`.

## Mitigación

- Deshabilitar `modeline` y `modelineexpr` en entornos sensibles.
- No abrir ficheros no confiables como root.
- Actualizar Vim.

## Detección

- Ficheros con líneas `vim:` o `ex:` inusuales.
- Procesos hijos de Vim ejecutando comandos.

## Referencias

- <https://vimhelp.org/options.txt.html#%27modeline%27>
- <https://attack.mitre.org/techniques/T1059/>
