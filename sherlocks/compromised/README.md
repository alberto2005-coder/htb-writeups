---
sherlock: Compromised
domain: DFIR / Red
difficulty: Easy
platform: Hack The Box
evidence: Captura de red de una red corporativa
tools: [Wireshark, tshark, NetworkMiner]
state: Retired
tags: [dfir, dfir-/-red]
---


# Compromised — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Hay indicios de tráfico malicioso en la red y al menos un equipo comprometido que contenía datos sensibles. Se entrega un PCAP para identificar el acceso inicial, la máquina afectada y qué se llevaron.

## Evidencias

- Un único `capture.pcap`.

## Investigación

1. **Panorama**: `Statistics → Conversations` para ver quién habla con quién y cuánto.

```bash
tshark -r capture.pcap -q -z conv,ip
tshark -r capture.pcap -q -z io,phs
```

2. **Acceso inicial**: buscar peticiones HTTP con parámetros sospechosos o credenciales en claro, y protocolos de administración expuestos (SMB, RDP, WinRM, FTP).

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

3. **Máquina comprometida**: el host que recibe la explotación y luego genera descargas o conexiones salientes nuevas. Cruzar IP con nombre NetBIOS/DNS.

4. **Exfiltración**: ficheros en `Export Objects → HTTP/SMB` y volúmenes anómalos en un flujo concreto (`Follow TCP Stream`).

5. **Cronología**: ordenar por `frame.time` los eventos clave (login, subida de webshell, descarga del dato).

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- En un PCAP, el acceso inicial suele estar en HTTP en claro o en un protocolo de administración sin cifrar.
- La huella del compromiso no es sólo la entrada: la **salida** de datos es la que confirma impacto.
- Exportar objetos revela lo que se descargó o robó sin necesidad de reconstruir el protocolo a mano.

## Tropiezos

- **Sólo un fragmento**: el PCAP puede empezar a mitad de la intrusión; no asumir que el primer paquete es el inicio.
- **TLS**: si el canal va cifrado, el análisis se apoya en metadatos (SNI, certificados, volúmenes, horas).
- **Relleno de escaneos**: separar el ruido de descubrimiento del tráfico de explotación.
