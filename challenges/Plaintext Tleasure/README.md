---
challenge: Plaintext Tleasure
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, credenciales, strings]
---

# Plaintext Tleasure — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una captura de tráfico con **HTTP sin cifrar**: en los flujos se ven credenciales de administrador y la propia flag en texto claro. Es el ejercicio más básico de análisis de red y sirve para fijar el reflejo de *follow the stream*.

## Evidencia

- `capture.pcap`.

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

## Tropiezos

- **`strings` engaña**: si el PCAP está comprimido por tramos o el texto va troceado, el `grep` no lo ve; el flujo sí.
- **Muchos flujos**: ordenar por tamaño y por método (`POST` primero).
- **HTTP/2**: si fuese binario, `strings` no sirve; hay que usar el disector.

## Lecciones

- HTTP sin TLS expone credenciales y datos: es la razón de ser de HSTS y de cifrar también lo interno.
- `Follow → HTTP Stream` es la herramienta básica del análisis de red.
- `strings` es un atajo; entender el flujo es lo que vale en un informe.
