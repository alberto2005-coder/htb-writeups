---
sherlock: Packet Puzzle
domain: DFIR / Red
difficulty: Medium
platform: Hack The Box
evidence: PCAP de una empresa de criptomonedas
tools: [Wireshark, tshark, NetworkMiner, CyberChef]
---

# Packet Puzzle — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Una pequeña empresa japonesa de intercambio de criptomonedas detecta actividad sospechosa en su red interna y exporta un PCAP. Hay que determinar si hubo compromiso y reconstruir los pasos del atacante.

## Evidencia

- `NetworkTraffic.pcap` dentro del ZIP habitual.

## Método

1. **Reconocimiento**: contar puertos tocados por el origen y ver cuántos responden.

```bash
tshark -r NetworkTraffic.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e ip.src -e ip.dst -e tcp.dstport | sort -u | wc -l
```

Un barrido con varios servicios (RDP, SMB, HTTP/S, WinRM y alguno de impresión) confirma un escaneo de descubrimiento.

2. **Servicio de entrada**: el primer puerto que responde y el protocolo que se usa después. En esta captura el acceso acaba en **RDP**, con intentos de credenciales.

```bash
tshark -r NetworkTraffic.pcap -Y 'tcp.port==3389' -T fields -e ip.src -e ip.dst | sort | uniq -c
```

3. **Sesión interactiva**: tras el acceso se ve una shell; los comandos (`whoami`, enumeración de disco) y sus respuestas viajan en claro en el canal.

4. **Movimiento y recolección**: nuevos flujos SMB internos, comparticiones montadas y copia de datos hacia el host del atacante.

5. **Cronología**: `frame.time` de la primera respuesta del servicio, del login correcto y de la primera transferencia de datos.

## Qué enseña

- Distinguir *scan* de *explotación*: el escaneo es simétrico y corto; la explotación genera sesión y datos.
- RDP permite inferir el sistema operativo y, con credenciales débiles, es puerta de entrada directa.
- Un PCAP bien ordenado por tiempo cuenta la historia completa sin necesidad de logs del host.

## Tropiezos

- **Muchos puertos, pocos paquetes**: no confundir un barrido rápido con explotación exitosa.
- **Sesiones largas**: los flujos RDP pesan mucho; filtrar por `tcp.stream` concreto.
- **Codificaciones**: los datos robados pueden ir comprimidos o en base64; probar `Export Objects` antes de decodificar a mano.
