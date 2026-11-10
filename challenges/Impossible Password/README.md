---
challenge: Impossible Password
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, gdb, strcmp, srand, radare2]
---

# Impossible Password — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.
> Las fuentes discrepan entre Very Easy y Easy; se documenta como Easy.

## TL;DR

Un ELF pide dos contraseñas. La primera se compara con una cadena fija (`SuperSeKretKey`) mediante un `strcmp` normal. La segunda **no**: el programa siembra `srand(time(0))`, reserva memoria y genera la cadena esperada con `rand()` en tiempo de ejecución, así que no existe en el binario. En vez de adivinarla, se pone un breakpoint en el segundo `strcmp` y se igualan los argumentos: la comparación devuelve 0 y el programa imprime la flag.

## Enunciado y superficie

- Reversing, retirado.
- Se entrega un único fichero: `impossible_password.bin`.
- Sin URL ni contenedor: todo ocurre en local.

## Reconocimiento

```bash
file impossible_password.bin
checksec --file=impossible_password.bin
strings -a impossible_password.bin | head -30
```

```text
impossible_password.bin: ELF 64-bit LSB executable, x86-64, dynamically linked
```

`strings` deja ver el mensaje de bienvenida y la primera contraseña, pero no la segunda: esa no está almacenada.

```bash
chmod +x impossible_password.bin
./impossible_password.bin
# *  (pide la primera)
# SuperSeKretKey
# ** (pide la segunda)
```

## Análisis del código

En `main` hay dos bloques de comparación:

```c
printf("* ");
__isoc99_scanf("%20s", buf1);
if (strcmp(buf1, "SuperSeKretKey") != 0) exit(1);

srand(time(0));
char *expected = malloc(0x11);
for (i = 0; i < 0x10; i++)
    expected[i] = rand() % 94 + 33;      /* imprimibles ASCII */
expected[0x10] = 0;

printf("** ");
__isoc99_scanf("%20s", buf2);
if (strcmp(buf2, expected) != 0) exit(1);

give_flag();
```

La segunda cadena depende de la hora: dos ejecuciones en segundos distintos esperan valores distintos. Por eso "la contraseña" no existe y el reto se llama así.

## Explicación del fallo

No hay corrupción de memoria ni un `strcmp` mal usado: el fallo es de **diseño de la comprobación**. El programa compara la entrada del usuario con un valor que él mismo calcula, y lo hace en el mismo espacio de direcciones. Cualquier atacante con un depurador puede hacer que ambos punteros apunten a la misma cadena, sin necesidad de predecir `rand()`.

Es el equivalente local de un servidor que valida el token comparándolo con el que él generó en memoria: la comprobación es correcta, pero el adversario controla el contexto.

## Reproducción local

```bash
gdb -q ./impossible_password.bin
```

```gdb
set disassembly-flavor intel
disassemble main
b *main+0x...        # dirección del segundo strcmp (la que sigue al segundo scanf)
run
SuperSeKretKey
AAAA
```

En el breakpoint:

```gdb
x/s $rdi
x/s $rsi
set $rdi = $rsi
continue
```

`x/s $rsi` muestra la cadena generada en esa ejecución: cambia cada segundo, lo que confirma el `srand(time(0))`.

## Explotación

Camino con GDB (el más corto):

```bash
gdb -q ./impossible_password.bin -ex 'b strcmp' -ex 'run' 
```

Con el breakpoint en `strcmp`, la primera llamada compara con `SuperSeKretKey`; se continúa (`c`), se envía cualquier cosa como segunda contraseña y, en la segunda parada, se igualan los registros:

```gdb
set $rdi = $rsi
continue
```

El programa cae en la rama correcta e imprime la flag.

Camino con radare2 (sin depurador interactivo):

```bash
r2 -A impossible_password.bin
pdf @ main
px @ <dirección de la cadena>
```

La flag se construye a partir de bytes que el binario transforma (XOR) antes de imprimir; localizada la rutina, se replica con un script de tres líneas en lugar de ejecutar el binario.

## Evidencia

- `x/s $rsi` con la cadena aleatoria y la salida final recortada.
- Sin flags reales: los valores viven en `private/`.

## Lecciones aprendidas

- `strcmp` con un valor generado en runtime no se "adivina": se intercepta.
- `srand(time(0))` hace la comprobación no determinista, pero también revela que el valor está en memoria antes de compararse.
- Igualar `$rdi`/`$rsi` en x86-64 es el atajo universal para saltarse una comparación de cadenas.
- `strings` no encuentra lo que se calcula: hay que leer el flujo, no solo el binario.

## Mitigaciones y detección

- En software real, una licencia no debe validarse comparando contra un valor calculado en el mismo proceso: usar firmas asimétricas verificadas con clave pública y ofuscar la comprobación no arregla el diseño.
- Detección (defensa): no aplica a un binario de CTF; en producto, telemetría de depuradores y de parches en memoria es ruido y no debe usarse como control.
- Para el análisis: documentar direcciones y offsets del build concreto; sin la versión exacta, el exploit no es reproducible.

MITRE: T1027.009? no — T1622 (debugger evasion) describe la técnica defensiva; aquí no se usa. Sin técnica ofensiva de ATT&CK aplicable.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/impossible-password>
- <https://dillonwu-97.github.io/csec-writeups/hackthebox/challenges/reversing/impossible-password>
- <https://sourceware.org/gdb/current/onlinedocs/gdb/>
- <https://cplusplus.com/reference/cstdlib/srand/>
