---
challenge: Find The Easy Pass
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, dotnet, dnspy, decompilation]
---

# Find The Easy Pass — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El ejecutable es .NET y valida la contraseña con una comparación directa. `dnSpy` o `ILSpy` descompilan el método y muestran la cadena esperada y la flag.

## Enunciado y superficie

- Reversing, Very Easy, retirado.
- Se entrega un `.exe` de Windows.
- El enunciado pide encontrar la contraseña.

```bash
file EasyPass.exe
strings -el EasyPass.exe | head
```

## Reconocimiento

- `file` lo identifica como PE .NET.
- `strings` muestra nombres de métodos y cadenas UTF-16.
- No hay packing evidente.

## Análisis del código

En `dnSpy`, se abre el ensamblado y se busca `Main` o el manejador del botón. El método compara la entrada con una constante mediante `String.op_Equality` o `Equals`.

La flag se construye a partir de la contraseña o se muestra en la rama correcta.

## Explicación del fallo

La validación ocurre en el cliente y la contraseña está embebida. No hay derivación ni comprobación remota: descompilar revela el secreto.

## Reproducción local

```bash
# Windows
EasyPass.exe
# Descompilar con dnSpy/ILSpy
```

- Localizar el método de validación.
- Poner un breakpoint en la comparación.
- Leer la constante y la llamada que muestra la flag.

## Explotación

Se introduce la contraseña recuperada y el programa muestra la flag. También se puede parchear el salto condicional para aceptar cualquier entrada.

## Evidencia

- `file` y captura de `dnSpy`.
- Cadena de comparación redactada.
- Ejecución correcta sin flag.

## Lecciones aprendidas

- .NET conserva metadatos y nombres.
- Un secreto en el cliente no es un secreto.
- Los breakpoints permiten observar la comparación sin parchear.

## Mitigaciones y detección

- Validar licencias en el servidor.
- Ofuscar solo como capa adicional, nunca como única protección.
- Firmar el binario y comprobar integridad.

## Referencias

- <https://www.hackthebox.com/challenges/Find%20The%20Easy%20Pass>
- <https://github.com/dnSpy/dnSpy>
