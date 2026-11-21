---
topic: SUID — desbordamiento de buffer por etapas
tags: [linux, suid, buffer-overflow, canary, aslr, ret2libc, one-gadget, ellingson]
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

## Caso real: Ellingson

En Ellingson, el SUID `/usr/bin/garbage` pedía una contraseña y desbordaba la pila con una entrada larga. `checksec` mostraba Partial RELRO, sin canary, NX activo y sin PIE, con ASLR completo. La explotación se dividió en dos etapas: primero se usó la PLT para filtrar una dirección de libc, después se calculó la base y se envió un segundo payload con `system` o un `one_gadget`. El binario no tenía PIE, así que las direcciones del código eran fijas; la única aleatorización que había que romper era la de libc. Este caso es un buen ejemplo de que “sin canary” no significa “sin protección”: NX y ASLR obligan a construir un ROP y a filtrar direcciones antes de ejecutar.

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

- [0xdf — Ellingson](https://0xdf.gitlab.io/2019/10/19/htb-ellingson.html)
- [0xdf — Calamity](https://0xdf.gitlab.io/2020/08/27/htb-calamity.html)
- [GDB — Debugging](https://sourceware.org/gdb/documentation/)
- [CWE-121 — Stack-based Buffer Overflow](https://cwe.mitre.org/data/definitions/121.html)
