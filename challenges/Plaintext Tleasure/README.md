---
challenge: Plaintext Tleasure
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, credenciales, strings]
type: Forensics
---

# Plaintext Tleasure — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una captura de tráfico con **HTTP sin cifrar**: en los flujos se ven credenciales de administrador y la propia flag en texto claro. Es el ejercicio más básico de análisis de red y sirve para fijar el reflejo de *follow the stream*.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Una captura de tráfico con **HTTP sin cifrar**: en los flujos se ven credenciales de administrador y la propia flag en texto claro. Es el ejercicio más básico de análisis de red y sirve para fijar el reflejo de *follow the stream*.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `capture.pcap`.

## Lecciones aprendidas

- **`strings` engaña**: si el PCAP está comprimido por tramos o el texto va troceado, el `grep` no lo ve; el flujo sí.
- **Muchos flujos**: ordenar por tamaño y por método (`POST` primero).
- **HTTP/2**: si fuese binario, `strings` no sirve; hay que usar el disector.

- HTTP sin TLS expone credenciales y datos: es la razón de ser de HSTS y de cifrar también lo interno.
- `Follow → HTTP Stream` es la herramienta básica del análisis de red.
- `strings` es un atajo; entender el flujo es lo que vale en un informe.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [pcap-triage](../../knowledge/forensics/pcap-triage.md)
## Método

1. **Atajo** (válido aquí, no siempre):

```bash
strings capture.pcap | grep -i 'HTB{'
```

2. **Método ordenado**: ver la jerarquía de protocolos y las conversaciones.

```bash
tshark -r capture.pcap -q -z io,phs
tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

3. **Seguir el flujo**: localizar el `POST` de login y hacer `Follow → HTTP Stream`; ahí están usuario, contraseña y la respuesta del servidor.

4. **Documentar**: qué credenciales se enviaron, a qué host y en qué momento (`frame.time`).
