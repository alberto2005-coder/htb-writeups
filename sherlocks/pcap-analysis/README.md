---
sherlock: PCAP Analysis
domain: DFIR / Red
difficulty: Very Easy
platform: Hack The Box
evidence: Una única captura de tráfico de un usuario
tools: [Wireshark, tshark, CyberChef]
---

# PCAP Analysis — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Una captura tomada del equipo de un usuario contiene un **chat en texto claro** y una **subida de fichero por HTTP**. Con unas 25 000 tramas, el reto es separar la conversación del ruido y extraer el fichero.

## Evidencia

- Un `Pcap_Analysis.pcapng`.

## Método

1. **Reducir el ruido**: `Statistics → Protocol Hierarchy` y `Conversations`.

```bash
tshark -r Pcap_Analysis.pcapng -q -z io,phs
```

2. **El chat**: filtrar por el protocolo de mensajería en claro y seguir el flujo.

```bash
tshark -r Pcap_Analysis.pcapng -Y 'tcp.port==6667 || http' -T fields -e _ws.col.Info | head
```

3. **La subida**: localizar el `POST` con `multipart/form-data` y exportar el objeto.

```bash
tshark -r Pcap_Analysis.pcapng -Y 'http.request.method=="POST"' -T fields -e http.request.uri
```

`File → Export Objects → HTTP` guarda el fichero; el tamaño se lee en la respuesta del servidor.

4. **El fichero**: `file` no reconoce firma (es datos), así que hay que mirar el contenido y la cabecera del multipart para saber qué se subió.

## Qué enseña

- En un PCAP grande, el primer paso siempre es reducir: protocolos, conversaciones, después contenido.
- El chat en claro y la subida HTTP dan nombre, intención y prueba de exfiltración.
- `Export Objects` evita reconstruir el multipart a mano.

## Tropiezos

- **Nombre del campo**: en el multipart, `name=` es el campo del formulario y `filename=` el nombre real del fichero.
- **Ruido de fondo**: tráfico de actualizaciones y DNS consume la mayor parte de las tramas; filtrar antes de leer.
- **Cifrado**: si la subida va por TLS, sólo quedan metadatos (SNI, tamaños, horas).
