---
challenge: Tear or Dear
category: Reversing
type: Reversing
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [reversing, dotnet, dnspy, windows, winforms]
---

# Tear or Dear — Hack The Box

[⏱ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Un formulario WinForms en .NET (`TearOrDear.exe`) pide usuario y contraseña. El código está lleno de métodos encadenados y nombres sin sentido, pero la comprobación final es una sola línea: `this.username == this.o && this.check1(s)`. Con **dnSpy de 32 bits** se pone un breakpoint ahí y se leen los dos valores esperados en locals; las credenciales son el cuerpo de la flag. No hace falta entender toda la ofuscación.

## Enunciado y superficie

- Categoría Reversing, dificultad Medium.
- Se entrega `TearOrDear.exe`, un PE32 GUI compilado desde C# .NET.
- El enunciado plantea un login que hay que superar; la flag es la credencial que lo abre.

## Reconocimiento

```bash
file TearOrDear.exe
```

```text
PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
```

Al ejecutarlo en Windows aparece un formulario con dos cajas, `User Name` y `Password`, y un botón `Login`. Cualquier combinación errónea deja `WRONG CREDENTIALS! Try Again...` en rojo.

## Análisis del código

dnSpy (o ILSpy/dotPeek) devuelve el C# casi original. Lo relevante:

- `button1_Click` llama a `kapa()`, que rellena `this.o` carácter a carácter mediante `linear` y `expo`.
- Después calcula `this.aa = Multiply(encrypted1(textBox_user.Text).Substring(0, 5), -1)` y le quita el último carácter.
- `Multiply` **invierte** la cadena y, de paso, asigna `this.username = textBox_pass.Text`.
- `check1` encadena `check2`, `check3`, `check4` y `check`, que al final compara `textBox_user.Text` con `this.aa`.
- La condición que decide es `this.username == this.o && this.check1(s)`.

Hay distracciones deliberadas: `oura = "p00f123#"`, `pepper = 10` y una recursión `encrypted1` que se corta a las diez llamadas. Ninguna cambia la comparación final.

## Explicación del fallo

La autenticación es **local y simétrica**: el programa construye en memoria los dos valores que espera (`this.o` para la contraseña, `this.aa` para el usuario) y los compara con la entrada. No hay servidor, hash ni secreto externo. Cualquier valor calculado en el cliente se puede leer con un depurador.

## Reproducción local

El binario necesita Windows o una VM con .NET Framework. Se ejecuta sin instalación y no abre puertos ni requiere red.

## Explotación

1. Abrir `TearOrDear.exe` con **dnSpy de 32 bits** (el proceso es de 32 bits; la versión de 64 no adjunta).
2. Poner un breakpoint en la línea `if (this.username == this.o && this.check1(s))` de `button1_Click`.
3. Introducir un usuario y una contraseña cualesquiera y pulsar `Login`.
4. Cuando pare el breakpoint, inspeccionar `this.o` y `this.aa`: son la contraseña y el usuario esperados.
5. Reconstruir `usuario:contraseña` y envolverlo en el formato de flag del reto.

Los valores concretos se guardan en `private/`; aquí no se publican.

## Evidencia

- `TearOrDear.exe`, PE32 .NET WinForms.
- Breakpoint en `button1_Click` con `this.o` y `this.aa` ya calculados.
- Credenciales y flag en `private/`.

## Lecciones aprendidas

- **Arquitectura de dnSpy**: con el binario de 32 bits hay que usar el dnSpy de 32 bits; si no, no se adjunta al proceso.
- **No perseguir la ofuscación**: `encrypted1` y `encrypted10` son ruido; la comparación final está en una línea.
- **`this.username` cambia**: `Multiply` lo sobrescribe con la contraseña, así que la comparación de usuario y contraseña se cruza. Leer los locals en el breakpoint evita confusiones.

## Mitigaciones y detección

- No validar credenciales en el cliente: cualquier comparación local es observable con un depurador.
- Si el binario necesita un secreto, que sea una clave pública y la verificación ocurra en servidor.
- Detección (si se usa como malware): assemblies .NET con nombres aleatorios, cadenas invertidas y comparaciones de credenciales embebidas; `dnSpy` y `ILSpy` son el triaje habitual.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/tear-or-dear/>
- <https://github.com/dnSpy/dnSpy>
- <https://github.com/icsharpcode/ILSpy>
