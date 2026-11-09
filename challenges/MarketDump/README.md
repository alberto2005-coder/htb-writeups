---
challenge: MarketDump
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, base58, exfiltracion]
type: Forensics
---

# MarketDump — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

En el PCAP, un atacante que pivotó por la web se lleva la base de datos de clientes por HTTP en claro. Todos los números de tarjeta empiezan igual menos uno: ese es el que interesa, y está codificado en **base58**.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

En el PCAP, un atacante que pivotó por la web se lleva la base de datos de clientes por HTTP en claro. Todos los números de tarjeta empiezan igual menos uno: ese es el que interesa, y está codificado en **base58**.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `MarketDump.zip` → `MarketDump.pcapng`.

## Lecciones aprendidas

- **base64 primero**: parece base64 y no lo es; probar base58 y base62 antes de descartar.
- **Muchos flujos**: filtrar por `http.response` y por tamaño, el volcado de la base de datos es el más grande.
- **Fichero .sql**: no hace falta importarlo a MySQL; con `strings` se lee perfectamente.

- Exportar objetos HTTP es la forma más rápida de recuperar lo exfiltrado en claro.
- La codificación no es cifrado: identificar el alfabeto (base58 evita `0OIl`) resuelve el reto.
- Mitigación: HTTPS en toda la ruta, sin excepciones para paneles internos.

## Mitigaciones y detección

- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [pcap-triage](../../knowledge/forensics/pcap-triage.md)
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
