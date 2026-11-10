---
challenge: MarketDump
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, base58, exfiltracion]
---

# MarketDump — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

En el PCAP, un atacante que pivotó por la web se lleva la base de datos de clientes por **HTTP en claro**. Todos los números de tarjeta empiezan igual menos uno; ese outlier no es base64, es **base58** y decodifica a la flag.

## Enunciado y superficie

`MarketDump.zip` → `MarketDump.pcapng`. Sin binario ni servidor: la evidencia es el tráfico y el volcado que viaja dentro.

## Reconocimiento

```bash
capinfos MarketDump.pcapng
tshark -r MarketDump.pcapng -Y 'http.response' -T fields -e frame.number -e ip.src -e content_type | head
```

`Statistics → Protocol Hierarchy` muestra HTTP y tráfico de base de datos: el atacante entró por la web y salió con un volcado.

## Explicación del fallo

`File → Export Objects → HTTP` lista un único objeto grande, `costumers.sql`. Su formato es `IssuingNetwork,CardNumber`:

```bash
strings costumers.sql | head -20
strings costumers.sql | awk -F, '{print $2}' | awk '{print substr($0,1,1)}' | sort | uniq -c
```

Casi todos los números comparten primer dígito; **uno** no. Ese valor tiene la longitud y el alfabeto de base58 (sin `0`, `O`, `I`, `l`), no de base64.

## Explotación

```bash
echo -n 'NVCijF7n6peM7a7yLYPZrPgHmWUHi97LCAzXxSEUraKme' | base58 -d
```

O con CyberChef, receta *From Base58*. La salida es la flag.

```text
HTB{<flag>}
```

No hace falta importar el `.sql` en MySQL: es texto plano y se lee con `strings`/`grep`.

## Evidencia

- Salidas recortadas; sin flags ni datos de tarjetas reales.
- Los valores reales viven en `private/`.

## Lecciones aprendidas

- **base64 primero, pero no único**: si falla el alfabeto estándar, probar base58/base62 antes de descartar.
- **El outlier es la señal**: en un volcado sintético, el valor distinto es el que interesa.
- **`Export Objects`** recupera el fichero completo sin reconstruir flujos a mano.
- **`.sql` es texto**: no hace falta montar una base de datos para leerlo.

- HTTP en claro convierte cualquier volcado en una descarga pública.
- La codificación no es cifrado: identificar el alfabeto resuelve el reto.
- Mitigación: HTTPS en toda la ruta, sin excepciones para paneles internos, y cifrado de datos de tarjeta en reposo.

## Nota de dificultad

HTB la lista como **Easy**; algún índice de la comunidad la recoge como **Medium**. Se deja Easy y se anota la discrepancia.
