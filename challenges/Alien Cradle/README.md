---
challenge: Alien Cradle
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, powershell, deobfuscation, download-cradle]
type: Forensics
---


# Alien Cradle — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Te dan `cradle.ps1`, un **PowerShell download cradle** ofuscado. Comprueba la identidad (`secret_HQ\Arth`), descarga un segundo stage con `WebClient` y lo ejecuta con `IEX`: ese payload remoto es un señuelo. La flag está **dentro del propio script**, construida concatenando cadenas.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Te dan `cradle.ps1`, un **PowerShell download cradle** ofuscado. Comprueba la identidad (`secret_HQ\Arth`), descarga un segundo stage con `WebClient` y lo ejecuta con `IEX`: ese payload remoto es un señuelo. La flag está **dentro del propio script**, construida concatenando cadenas.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `cradle.ps1` (una sola línea muy larga).

## Lecciones aprendidas

- **Ejecutarlo**: no hay que lanzarlo; basta analizarlo. Ejecutar código de un reto es innecesario.
- **Ofuscación**: puede haber variables intermedias y `-join`; seguir el flujo de asignaciones.
- **Una sola línea**: sin formatear, los literales se pierden de vista.

- Un *cradle* es el patrón clásico de staging: descarga y ejecuta en memoria.
- La ofuscación por concatenación se deshace leyendo, no ejecutando.
- Un `if` con identidad de usuario es detección de sandbox y de objetivo.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)

## Método

1. **Formatear** el script para leerlo: está minificado.

```bash
sed 's/;/;\n/g' cradle.ps1 | head -40
```

2. **Identificar el patrón**: `New-Object Net.WebClient`, `.DownloadString(...)` y `IEX(...)` son la firma de un *cradle*; el `if` inicial con `WindowsIdentity.GetCurrent().Name` es un *gate* para ejecutarse sólo en el host objetivo.

3. **Ignorar el señuelo**: el contenido remoto no se obtiene (y no hace falta). La información está en el código local.

4. **Reconstruir la cadena**: al final hay algo como `$f='H'+'T'+'B'+'{p0w3rs'+'h3ll'+...`. Se concatenan los literales en orden.

```powershell
$f = 'H'+'T'+'B'+'...'   # evaluar sólo esta asignación
```

5. **Leer** el resultado: es la flag.
