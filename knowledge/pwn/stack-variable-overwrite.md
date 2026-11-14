---
topic: Sobrescritura de variables en la pila
tags: [pwn, stack, buffer-overflow, gets, variable-overwrite, pwntools]
---

# Sobrescritura de variables en la pila

[🌐 English](stack-variable-overwrite.en.md) | **Español**

## Concept

Un desbordamiento de buffer no siempre busca controlar la dirección de retorno. Si una variable local decide una rama de seguridad y está contigua al buffer, escribir más bytes de los reservados la sobrescribe y activa el código privilegiado.

## Cuándo aplica

- `gets`, `strcpy`, `sprintf` o `read` con longitud incorrecta.
- Variables locales como `is_admin`, `check` o `authenticated`.
- Código muerto que lee la flag o ejecuta una función.
- Falta de canary y de comprobaciones de longitud.

## Procedimiento

1. Desensamblar `main` y dibujar el marco de pila.
2. Medir el offset entre el buffer y la variable objetivo.
3. Comprobar el orden y el tamaño de las variables.
4. Construir el payload con relleno y el valor deseado.
5. Enviarlo y verificar la rama.

```python
from pwn import *
payload = b"A" * 60 + p64(0x1337bab3)
p = process("./challenge")
p.sendline(payload)
print(p.recvall())
```

## Variantes

- Variable de 4 bytes alineada tras el buffer.
- Cambio de un puntero a función local.
- Sobrescritura de un índice o de un tamaño.
- Desbordamiento que también pisa el canary y el return address.

## Limitaciones

- El compilador puede reordenar o alinear las variables.
- El canary detecta la corrupción si está entre el buffer y el objetivo.
- PIE no afecta si solo se cambia un valor.
- La entrada puede terminar en un byte nulo.

## Mitigación y detección

- Usar funciones con límite y comprobar la longitud.
- Compilar con canary, NX y PIE.
- No usar variables locales para decisiones de seguridad.
- Alertar de crashes y de entradas anormalmente largas.

## Referencias

- <https://man7.org/linux/man-pages/man3/gets.3.html>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://github.com/Gallopsled/pwntools>
