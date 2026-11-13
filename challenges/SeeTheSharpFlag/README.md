---
challenge: SeeTheSharpFlag
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, xamarin, dotnet, decompilation]
---

# SeeTheSharpFlag — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app usa Xamarin/.NET. Los ensamblados .NET viajan dentro del APK y se pueden descompilar con ILSpy o dnSpy. La comprobación y la flag aparecen en el código administrado.

## Enunciado y superficie

- Mobile, Easy, retirado.
- Se entrega un APK de una app Xamarin.
- La pantalla solicita una entrada y valida el resultado.

```bash
unzip -l app.apk | grep -Ei 'assemblies|dll|mono'
```

## Reconocimiento

- El APK contiene `assemblies/` y bibliotecas de Mono.
- Los `.dll` son ensamblados .NET, no código nativo.
- `file` sobre los ensamblados confirma el formato PE/.NET.

```bash
unzip -o app.apk -d apk
find apk -iname '*.dll' -o -iname '*.exe'
file apk/assemblies/*.dll
```

## Análisis

Se abre el ensamblado principal con ILSpy o `ilspycmd`. Se buscan clases de validación, constantes y llamadas a comparación. La flag puede estar en una constante o construirse a partir de varias cadenas.

```bash
ilspycmd apk/assemblies/SeeTheSharpFlag.dll > decompiled.cs
grep -nE 'flag|password|check|Equals|Compare' decompiled.cs | head -n 40
```

## Explotación

1. Extraer los ensamblados del APK.
2. Identificar el método que decide el éxito.
3. Leer la constante o reproducir la transformación.
4. Introducir el valor en la app o calcular la flag.

No hace falta ejecutar la app ni parchear el APK si la lógica es estática.

## Evidencia

- Lista de ensamblados.
- Fragmento del método de validación.
- Valor calculado y pantalla de éxito, con la flag redactada.

## Lecciones aprendidas

- Xamarin compila a IL, no a bytecode Java.
- Los ensamblados dentro del APK son código de plena confianza para el analista.
- La ofuscación .NET se revierte con las herramientas adecuadas.

## Mitigaciones y detección

- No guardar secretos en ensamblados cliente.
- Validar en servidor y usar atestación.
- Ofuscar con control de integridad.
- Detectar APKs recompiladas y ensamblados modificados.

## Referencias

- <https://www.hackthebox.com/challenges/SeeTheSharpFlag>
- <https://github.com/icsharpcode/ILSpy>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1552/>
