---
challenge: Plaintext Tleasure
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, credenciales, tshark]
type: Forensics
---

# Plaintext Tleasure — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una captura de tráfico con **HTTP sin cifrar**. El reto es el ejercicio más básico de análisis de red: separar los flujos útiles del ruido y leerlos. Las credenciales y el objeto de interés están en el cuerpo de las peticiones, en texto claro, sin nada que descifrar.

## Enunciado y superficie

- Categoría **Forensics**; el material es una única captura (`capture.pcap` en el paquete del reto).
- No hay servicio al que atacar ni código que revisar: todo lo que hace falta está en el fichero.

## Reconocimiento

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z io,phs
```

`capinfos` da número de tramas y duración; la jerarquía de protocolos dice si hay TLS (y entonces no habría nada legible) o HTTP en claro, que es el caso.

## Análisis

1. **Quedarse con HTTP**:

```bash
tshark -r capture.pcap -Y 'http.request' \
  -T fields -e frame.number -e http.request.method -e http.request.uri -e http.host
```

2. **Ordenar por método**: los `POST` primero, que es donde viajan credenciales y cuerpos.

3. **Seguir el flujo bueno**:

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,<stream>
```

En el `POST` aparece el par usuario/contraseña del formulario; la respuesta del servidor trae el objeto que se estaba transfiriendo.

4. **Exportar lo transferido** si hay fichero:

```bash
tshark -r capture.pcap --export-objects http,exported/
file exported/*
```

## Explicación del fallo

La aplicación envía credenciales por **HTTP sin TLS**: cualquiera con acceso al segmento (o a una captura) las lee sin romper nada. No hay fallo criptográfico que explotar; el fallo es de diseño del canal.

## Evidencia

- `capture.pcap`.
- En el informe: método, URI, host y credenciales **redactadas**.

## Lecciones

- `strings` no sustituye a seguir el flujo: el cuerpo va troceado en segmentos TCP y el `grep` no lo ve.
- Ordenar por método y por tamaño ahorra abrir decenas de flujos.
- HTTP en claro expone credenciales y datos: es la razón de existir de HSTS y de cifrar también el tráfico interno.
- Si el flujo fuera TLS, sólo quedarían metadatos (SNI, tamaños, horas) y el reto no tendría solución por lectura directa.

## Mitigaciones y detección

- TLS en todo el sitio, HSTS y redirección desde HTTP; certificados válidos también en servicios internos.
- Nunca enviar credenciales por formularios servidos en claro; `Secure` en cookies de sesión.
- Detección: credenciales en `POST` sobre HTTP, y tráfico HTTP hacia hosts que deberían hablar sólo HTTPS.

## Referencias

- [Wireshark — Follow TCP Stream](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvFollowStreamSection.html)
- [Hack The Box — Plaintext Tleasure](https://app.hackthebox.com/challenges/Plaintext%20Tleasure)
