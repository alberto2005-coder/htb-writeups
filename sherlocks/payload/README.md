---
sherlock: Payload
domain: Análisis de malware
difficulty: Easy
platform: Hack The Box
evidence: Ejecutable de Windows con payload cifrado
tools: [Detect It Easy, x64dbg, PE-bear, CyberChef]
state: Retired
tags: [dfir, análisis-de-malware]
---


# Payload — Hack The Box

[LOG] Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un ejecutable de Windows, compilado con **MinGW**, descifra en tiempo de ejecución el payload que realmente ejecuta. En lugar de reproducir a mano el algoritmo de descifrado, el ejercicio propone **saltarlo con un depurador** y dejar que el propio malware haga el trabajo.

## Evidencias

- Un `.exe` de 32/64 bits sin firma.

## Investigación

1. **Triage estático**: compilador y secciones.

```bash
file sample.exe; strings -n 6 sample.exe | head -40
```

MinGW deja rastros de `gcc`/`mingw` y una tabla de imports mínima; el payload suele vivir en `.rdata`/`.data`.

2. **Punto de entrada**: abrir en **x64dbg**, ir a `EntryPoint` y seguir las llamadas que reciben un buffer y una longitud.

3. **Bucle de descifrado**: normalmente XOR/RC4/AES sobre una región de memoria. Localizar la instrucción que escribe el byte descifrado y poner un **breakpoint después del bucle**.

4. **Saltar el cifrado**: cuando el buffer ya está en claro, volcar la región (`Follow in Dump` → `Binary → Save to file`) o cambiar un salto para ejecutar el payload descifrado.

5. **Analizar el volcado**: `strings` y un segundo pase en el depurador para ver la URL de C2, el nombre del servicio o los comandos.

## Conclusiones

[LOG] Hack The Box

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- La ejecución dinámica ahorra reimplementar algoritmos: el malware descifra por ti.
- Un breakpoint tras el bucle de descifrado es la técnica estándar contra *packers* caseros.
- Los binarios MinGW no llevan firma ni metadatos: el triage empieza por el compilador.

## Tropiezos

- **ASLR/PIE**: si el binario se reubica, usar direcciones relativas al módulo.
- **Antidepuración**: `IsDebuggerPresent`, `NtQueryInformationProcess` o comprobaciones de tiempo; parchear el salto.
- **Ejecutar el payload**: extraer y analizar estáticamente, nunca lanzarlo fuera de la VM aislada.
