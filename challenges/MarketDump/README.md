---
challenge: MarketDump
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, base58, exfiltracion]
---

# MarketDump — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

En el PCAP, un atacante que pivotó por la web se lleva la base de datos de clientes por HTTP en claro. Todos los números de tarjeta empiezan igual menos uno: ese es el que interesa, y está codificado en **base58**.

## Evidencia

- `MarketDump.zip` → `MarketDump.pcapng`.

## Método

1. **Panorama del tráfico**: `Statistics → Protocol Hierarchy`. Además de HTTP aparece tráfico de base de datos, lo que confirma el pivote por la web.

2. **Extraer el objeto**: `File → Export Objects → HTTP` muestra `costumers.sql`. Se guarda y se inspecciona:

```bash
strings costumers.sql | head -20
```

El formato es `IssuingNetwork,CardNumber`. Casi todos los números empiezan por `3`; uno no.

3. **Decodificar el outlier**: la cadena atípica no es base64 (falla), es **base58**:

```bash
echo -n '<cadena>' | base58 -d
```

También vale CyberChef con la receta *From Base58*.

4. **Contexto**: seguir el flujo TCP de la respuesta del servidor (`Follow → TCP Stream`) muestra la descarga completa y quién la pidió.

## Tropiezos

- **base64 primero**: parece base64 y no lo es; probar base58 y base62 antes de descartar.
- **Muchos flujos**: filtrar por `http.response` y por tamaño, el volcado de la base de datos es el más grande.
- **Fichero .sql**: no hace falta importarlo a MySQL; con `strings` se lee perfectamente.

## Lecciones

- Exportar objetos HTTP es la forma más rápida de recuperar lo exfiltrado en claro.
- La codificación no es cifrado: identificar el alfabeto (base58 evita `0OIl`) resuelve el reto.
- Mitigación: HTTPS en toda la ruta, sin excepciones para paneles internos.
