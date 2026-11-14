---
topic: Fuerza bruta de ASLR
tags: [privesc, aslr, ret2libc, 32-bit, buffer-overflow]
---

# Fuerza bruta de ASLR

[🌐 English](aslr-brute-force.en.md) | **Español**

## Concepto

En binarios de 32 bits, la entropía de ASLR puede ser baja: la base de libc cambia solo unos cientos de posiciones. Si el proceso se puede reiniciar sin consecuencias, un bucle de ret2libc acierta la dirección con suficiente probabilidad.

## Cuándo aplica

- SUID de 32 bits sin PIE y con NX.
- ASLR habilitado pero con `randomize_va_space=2` y rango pequeño.
- Proceso que no bloquea reintentos ni registra fallos.

## Procedimiento

1. Confirmar NX, ausencia de canario y PIE.
2. Medir el rango de la base de libc con `ldd`.
3. Calcular offsets de `system`, `exit` y `/bin/sh`.
4. Repetir el payload hasta obtener shell.

```bash
for i in $(seq 1 2000); do
  /usr/local/bin/ovrflw "$(python -c 'print "A"*112 + "<system>" + "<exit>" + "<binsh>"')" && break
done
```

## Variantes

- Fuerza bruta de la dirección de retorno en 32 bits.
- `ret2plt` cuando libc no se puede filtrar.
- Ataque de fuerza bruta sobre el canario con `fork()`.

## Limitaciones

- La probabilidad crece lento si la entropía es alta.
- El servicio debe reiniciarse o aceptar múltiples conexiones.
- Los crashes pueden alertar o detener el proceso.

## Mitigación y detección

- Compilar con PIE y canario.
- Usar ASLR de 64 bits y `mmap` aleatorio.
- Limitar reintentos y monitorizar crashes.
- Alertar de ejecuciones repetidas de SUID con payloads largos.

## Referencias

- <https://www.exploit-db.com/docs/english/28553-linux-classic-return-to-libc-&-return-to-libc-chaining-tutorial.pdf>
- <https://attack.mitre.org/techniques/T1068/>
