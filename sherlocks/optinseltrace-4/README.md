---
sherlock: OpTinselTrace-4
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, printer, pjl, ssh, aes]
---

# OpTinselTrace-4 — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

La investigación llega a un servidor de impresión. Se entrega un ZIP cifrado con AES que contiene una captura de red del servidor. Hay que extraerla, identificar el tráfico de impresión (PJL) y la sesión SSH, y reconstruir qué se imprimió o exfiltró.

## Evidencias

- ZIP cifrado con AES (no usar `unzip`; usar 7-Zip).
- `traffic.pcap`/`capture.pcapng` del servidor de impresión.
- Conversaciones PJL y SSH.
- Posibles trabajos de impresión y credenciales.

```bash
7z x optinseltrace-4.zip
capinfos capture.pcap
```

## Investigación

### 1. Inventario y triaje

Se identifican los hosts y protocolos:

```bash
tshark -r capture.pcap -q -z conv,tcp
tshark -r capture.pcap -Y 'pjl || ssh' -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport
```

PJL suele ir al puerto 9100; SSH al 22. Se separan los flujos y se reconstruyen.

### 2. Línea temporal

- Conexión al servidor de impresión.
- Trabajo PJL con nombre de fichero y usuario.
- Sesión SSH y comandos ejecutados.
- Transferencia de datos o impresión de un documento sensible.

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,<STREAM>
```

### 3. Artefacto clave

El flujo PJL contiene el nombre del trabajo y, a veces, el contenido en claro. La sesión SSH puede incluir credenciales o comandos de copia. El ZIP AES obliga a usar 7-Zip; `unzip` falla con “unsupported compression method”.

```text
ZIP AES -> PCAP -> PJL (trabajo) + SSH (acceso)
```

## Conclusiones

- El servidor de impresión se usó para imprimir o extraer un documento.
- La sesión SSH permitió ejecutar comandos en el servidor.
- Los IOCs son IPs, puertos, nombre del trabajo, usuario y ruta.
- El cifrado del ZIP es solo una capa de transporte, no de la evidencia.

## Lecciones

- 7-Zip maneja AES; `unzip` no.
- PJL puede exponer nombres y contenido de trabajos.
- SSH en una captura permite reconstruir comandos si no está cifrado con clave desconocida.
- Los servidores de impresión son un punto ciego frecuente.

## Referencias

- <https://inksec.io/blue-team/sherlocks/optinseltrace-4>
- <https://www.7-zip.org/>
- <https://attack.mitre.org/techniques/T1052/>
