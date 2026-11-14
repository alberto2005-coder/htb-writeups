---
topic: ELF analysis
tags: [reversing, elf, ghidra, gdb, readelf, binary]
---

# ELF analysis

[🌐 English](elf-analysis.en.md) | **Español**

## Concepto

Un binario ELF se analiza en tres capas: cabeceras y símbolos, código desensamblado y comportamiento en ejecución. `readelf`, `objdump`, Ghidra y GDB permiten pasar de la estructura estática a la lógica y a la explotación.

## Cuándo aplica

- Retos de reversing o pwn.
- Binario sin código fuente.
- Búsqueda de funciones de validación.
- Análisis de protecciones antes de un exploit.

## Procedimiento

1. Identificar arquitectura, bits y enlazado.
2. Revisar símbolos, imports y strings.
3. Desensamblar o descompilar en Ghidra.
4. Ejecutar en GDB y observar llamadas.
5. Documentar la lógica y las protecciones.

```bash
file ./binary
checksec --file=./binary
readelf -h ./binary
readelf -s ./binary | head
objdump -d -M intel ./binary | head
gdb -q ./binary
```

## Variantes

- Binario estático o dinámico.
- Stripped con símbolos eliminados.
- PIE, NX, canary y RELRO.
- Comparación de ramas y funciones criptográficas.

## Limitaciones

- La descompilación puede perder tipos.
- El binario puede estar empaquetado.
- La arquitectura puede requerir emulación.
- GDB necesita permisos y entorno compatible.

## Mitigación y detección

- No confiar en la ofuscación como protección.
- Firmar y verificar binarios.
- Aplicar protecciones del compilador.
- Monitorizar ejecución de binarios no firmados.

## Referencias

- <https://man7.org/linux/man-pages/man5/elf.5.html>
- <https://ghidra-sre.org/>
- <https://sourceware.org/gdb/documentation/>
