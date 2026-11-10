---
sherlock: PCAP Analysis
domain: SOC / DFIR de red
difficulty: Very Easy
platform: Hack The Box
state: Retired
evidence: Una única captura de tráfico de un usuario
tools: [Wireshark, tshark, capinfos, xxd]
tags: [dfir, soc, pcap, http, file-upload]
---

# PCAP Analysis — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

«Hemos capturado este tráfico del equipo de P13». Eso es todo lo que da el enunciado: una captura con miles de tramas en la que conviven un **chat en texto claro** en un puerto poco habitual y una **subida de fichero por HTTP** sin cifrar.

## Evidencias

```text
Pcap_Analysis.zip     (contraseña en la página del Sherlock)
Pcap_Analysis.pcapng
```

## Investigación

### 1. Medir antes de leer

```bash
unzip -P <password> PCAP_Analysis.zip
capinfos Pcap_Analysis.pcapng
tshark -r Pcap_Analysis.pcapng -q -z io,phs
```

`capinfos` da número de paquetes, duración y tamaños; la jerarquía de protocolos dice qué merece la pena filtrar. En una captura de este tamaño, abrirla sin filtrar es perder el tiempo.

### 2. El chat

El identificador del Sherlock es el **puerto no estándar**: no es IRC ni un protocolo conocido, es texto plano sobre TCP. Al filtrar por ese puerto y reconstruir el payload se lee la conversación y se obtienen los dos extremos:

```bash
tshark -r Pcap_Analysis.pcapng -Y 'tcp.port==250 && tcp.len>1' \
  -T fields -e ip.src -e ip.dst -e tcp.payload | xxd -r -p
```

Los nombres que aparecen en los mensajes identifican a cada interlocutor y sus IP; el emisor del chat es el mismo host que después sube el fichero.

### 3. La subida

```bash
tshark -r Pcap_Analysis.pcapng -Y 'http.request.method=="POST"' \
  -T fields -e ip.src -e ip.dst -e http.request.uri -e http.content_length
```

El `POST` es `multipart/form-data` contra un Apache en otra subred. Para leer la petición completa y la respuesta (que revela el directorio de destino):

```bash
tshark -r Pcap_Analysis.pcapng -q -z follow,tcp,ascii,<stream>
```

### 4. El fichero

`File → Export Objects → HTTP` guarda el objeto; el fichero se llama `file`, pesa unos 107 KB y su contenido es prácticamente aleatorio, es decir, ya está cifrado o comprimido. El tamaño de la transferencia sale restando el primer y el último paquete del flujo.

## Conclusiones

- El emisor del chat y el de la subida son la misma estación: un usuario que conversa y exfiltra en la misma sesión de captura.
- La conversación va en claro en un puerto no estándar, y la subida por HTTP sin TLS: ambos canales son legibles sin descifrar nada.
- El fichero subido es opaco (alta entropía), así que la evidencia útil es el **quién, a dónde y cuándo**, no el contenido.

## Lecciones

- `capinfos` y la jerarquía de protocolos convierten una captura grande en un plan de filtros.
- Un puerto raro con texto legible no es «tráfico desconocido»: es un protocolo casero y se lee siguiendo el flujo.
- La respuesta del servidor suele confesar más que la petición: ruta de guardado, versión de Apache, código de estado.
- Un objeto de alta entropía no se «descifra» sin más datos; se documenta como IOC y se correlaciona.
