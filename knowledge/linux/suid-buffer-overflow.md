---
topic: SUID — desbordamiento de buffer por etapas
tags: [linux, suid, buffer-overflow, canary, aslr]
---

# SUID — desbordamiento de buffer por etapas

[🌐 English](suid-buffer-overflow.en.md) | **Español**

## Concepto

Un binario SUID que lee más datos de los que su buffer admite permite sobrescribir la pila. Con canary y ASLR se encadenan etapas: una fuga de direcciones, el cálculo del canary y un segundo desbordamiento que controla el retorno. El objetivo es ejecutar una shell con el UID efectivo de root.

## Cuándo aplica

- Un binario con SUID bit acepta entrada de usuario.
- `checksec` muestra NX y canary, pero no PIE o hay una fuga.
- El binario se puede depurar localmente con la misma versión.

## Procedimiento

1. Copiar el binario y ejecutar `checksec`.
2. Provocar un crash y medir el offset con `patternget`.
3. Filtrar canary, base de libc o PIE en una primera etapa.
4. Construir el ROP o ret2libc y ejecutar la segunda etapa.

## Comandos

```bash
find / -perm -4000 -type f 2>/dev/null
checksec --file=/usr/local/bin/<BIN>
gdb -q /usr/local/bin/<BIN>
patternget 100
python3 exploit.py
id
```

## Variantes

- Ret2libc si NX está activo.
- ROP con `pop rdi; ret` para `system`.
- Aprovechar un `gets` o `read` con tamaño incorrecto.

## Limitaciones

- El binario puede estar compilado con PIE y full RELRO.
- La versión remota debe coincidir con la local.
- El entorno puede limitar `ptrace` o `execve`.

## Mitigación

- Compilar con `-fstack-protector-strong`, PIE y RELRO completo.
- Retirar SUID innecesarios.
- Validar longitudes y usar funciones seguras.

## Detección

- Crashes de binarios SUID con entradas largas.
- Core dumps de procesos privilegiados.
- Ejecución de shells desde un binario SUID.

## Referencias

- [0xdf — Calamity](https://0xdf.gitlab.io/2020/08/27/htb-calamity.html)
- [GDB — Debugging](https://sourceware.org/gdb/documentation/)
- [CWE-121 — Stack-based Buffer Overflow](https://cwe.mitre.org/data/definitions/121.html)
