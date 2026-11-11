---
title: ".NET: triaje, dnSpy y depuración"
tags: [reversing, dotnet, dnspy, ilspy, windows]
---

# .NET: triaje, dnSpy y depuración

[🇬🇧 English](dotnet-dnspy.en.md) | **Español**

## 1. Cuándo mirar aquí

Un ejecutable de Windows pide credenciales, valida una licencia o esconde una cadena. Si es .NET, el código intermedio (CIL) se descompila casi al fuente original y el análisis deja de ser arqueología.

## 2. Identificarlo

```bash
file sample.exe
```

`PE32 executable (GUI) Intel 80386 Mono/.Net assembly` confirma .NET. También ayuda `strings -el` (cadenas UTF-16) y Detect It Easy, que marca el runtime y el obfuscador.

## 3. Herramientas

- **dnSpy / dnSpyEx**: descompilador y depurador en la misma ventana. Editar y continuar, breakpoints, inspección de locales.
- **ILSpy**: descompilador rápido, buena vista de IL y de recursos.
- **dotPeek**: alternativa de JetBrains.
- **de4dot**: limpieza de obfuscadores comunes antes de descompilar.

Arquitectura: si el proceso es de 32 bits, usar dnSpy de 32 bits; el de 64 no se adjunta. Es el error más habitual.

## 4. Flujo de trabajo

1. Abrir el assembly y localizar el punto de entrada (`Main`) o el manejador del botón.
2. Leer la clase del formulario: los campos guardan los valores esperados.
3. Poner breakpoint en la comparación final, no en cada método.
4. Ejecutar con datos de prueba y leer los locales (`this.o`, `this.aa`).
5. Reconstruir la condición y documentar la ruta.

Ejemplo de condición que resume un formulario entero:

```csharp
if (this.username == this.o && this.check1(s)) { ... }
```

## 5. Ofuscación

Nombres aleatorios, cadenas cifradas, flujo plano y llamadas encadenadas son ruido. Antes de perseguirlas, busca la comparación que decide: suele ser una línea. `de4dot` recupera nombres cuando el protector es conocido; si no, el depurador sigue siendo suficiente.

## 6. Límites

- Un assembly firmado o con *anti-tamper* puede negarse a ejecutarse bajo depurador; en un CTF, parchear la comprobación es aceptable, en malware no.
- `NativeAOT` y `ReadyToRun` ya no son CIL puro: parte del código es nativo y requiere Ghidra/IDA.
- Los recursos incrustados (`Resources.resx`) pueden contener la clave; revísalos antes de concluir.

## 7. Mitigación y detección (lado real)

- No validar credenciales en cliente: cualquier comparación local se lee con un depurador.
- Si hace falta un secreto, usar clave pública y verificación en servidor.
- Detección: assemblies con nombres aleatorios, cadenas cifradas y P/Invoke a `VirtualAlloc`/`CreateRemoteThread` son señales de malware .NET; dnSpy y ILSpy son el triaje estándar.

Referencias: documentación de dnSpy, ILSpy, de4dot y ECMA-335 (CIL).
