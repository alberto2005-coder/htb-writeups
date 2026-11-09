---
sherlock: BFT
domain: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, mft, ntfs, timestomp, zone-identifier, resident-data, mftecmd]
---

# BFT — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Solo hay un fichero: la **$MFT** (Master File Table) en crudo de un equipo comprometido. Con ella hay que reconstruir la intrusión: qué se descargó, dónde se extrajo, qué script se ejecutó y a qué C2 llama.

## Evidencias

```text
mft.raw
```

## Investigación

### 1. Parsear la MFT

```bash
MFTECmd.exe -f mft.raw --csv out/
```

Se abre el CSV en Timeline Explorer. Cada registro son 1024 bytes, así que la posición de un registro es `entrada × 1024`.

### 2. La entrega

Se filtra por `ParentPath` de la carpeta de descargas del usuario y se ordena por tiempo: aparece un **ZIP** descargado y, minutos después, una carpeta extraída con el mismo nombre base. El nombre del ZIP es la primera prueba de la entrega.

El flujo de zona (`Zone.Identifier`) marca el fichero como descargado de internet: `Mark-of-the-Web`, que sobrevive al descomprimir solo si el contenedor lo propaga.

### 3. El script y el timestomping

Dentro de la carpeta extraída hay un `.bat` con nombre de factura en una ruta anidada sospechosa (`invoice/invoices/`). Se comparan las dos parejas de timestamps del registro:

- `$STANDARD_INFORMATION` (lo que ve el usuario)
- `$FILE_NAME` (lo que mantiene NTFS al crear el fichero)

Si el `$SI` es mucho más antiguo que `$FN`, alguien lo retocó: **timestomping** (T1070.006).

### 4. Contenido residente en la MFT

Los ficheros pequeños viven **dentro** del propio registro, en el atributo `$DATA` residente. No hace falta recuperar el fichero del disco: con un editor hexadecimal se salta a `entrada × 1024` y se lee el contenido.

```text
offset = 23436 * 1024 = 0x16E3000
```

Ahí está el `.bat` completo, con la IP y el puerto del C2 en texto claro.

## Conclusiones

- Entrega: ZIP descargado desde internet a la carpeta del usuario.
- Ejecución: script `.bat` que se hace pasar por factura.
- Evasión: timestomping para que el script parezca antiguo.
- C2: IP y puerto legibles en el `$DATA` residente del registro.

## Lecciones

- La MFT da nombre, ruta padre, tamaño y **varias** parejas de timestamps: es una línea temporal completa sin abrir el disco.
- Los ficheros pequeños se leen desde la MFT; el hex editor sustituye al carving.
- Comparar `$SI` con `$FN` es la forma estándar de detectar timestomping.
