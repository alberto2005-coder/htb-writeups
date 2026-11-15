---
topic: PHP — desbordamiento de enteros en extensiones nativas
tags: [linux, php, extension, integer-overflow, gdb]
---

# PHP — desbordamiento de enteros en extensiones nativas

[🌐 English](php-extension-integer-overflow.en.md) | **Español**

## Concepto

Una extensión PHP escrita en C puede calcular índices o tamaños con enteros sin comprobar. Un valor grande desborda y produce un índice negativo o un tamaño menor del real, lo que permite sobrescribir memoria de la pila o del heap. Si el proceso PHP corre como root o con privilegios, la ejecución es directa.

## Cuándo aplica

- La aplicación carga una extensión nativa propia.
- La extensión procesa un entero controlado por el usuario.
- Hay una versión local del binario para depurar.

## Procedimiento

1. Identificar la extensión y la función expuesta.
2. Reproducir el cálculo con valores límite.
3. Depurar con GDB y localizar la variable sobrescrita.
4. Construir el payload y controlar el flujo.

## Comandos

```bash
php -m
php -i | grep extension_dir
gdb -q -p <PID>
# Valor que desborda el índice
curl "http://<HOST>/index.php?n=9223372036854775807"
checksec --file=$(which php)
```

## Variantes

- Desbordar un `int` usado como tamaño de `memcpy`.
- Aprovechar un índice negativo para escribir antes del buffer.
- Combinar con una fuga de direcciones del propio PHP.

## Limitaciones

- La extensión puede validar el rango.
- El binario puede tener ASLR/PIE.
- El entorno de producción puede diferir del local.

## Mitigación

- Validar enteros y usar comprobaciones de límites.
- Compilar con `-fstack-protector` y `-D_FORTIFY_SOURCE=2`.
- Ejecutar PHP con un usuario sin privilegios.

## Detección

- Valores extremos en parámetros numéricos.
- Crashes de PHP con segfault.
- Extensiones nativas sin actualizar.

## Referencias

- [0xdf — Ouija](https://0xdf.gitlab.io/2024/05/18/htb-ouija.html)
- [PHP — Writing extensions](https://www.php.net/manual/en/internals2.php)
- [CWE-190 — Integer Overflow](https://cwe.mitre.org/data/definitions/190.html)
