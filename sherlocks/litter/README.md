---
sherlock: Litter
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, dns-tunneling, dnscat2, exfiltration]
---

# Litter — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un host de pruebas compartido, fuera de la red corporativa pero con acceso a recursos internos, ha sido comprometido. Se entrega un ZIP con evidencias y un PCAP del tráfico sospechoso; hay que determinar qué herramienta usó el atacante, cómo exfiltró datos y cuántos registros se llevó.

## Evidencias

- Un ZIP protegido con contraseña (la del escenario).
- `suspicious_traffic.pcap`.
- Un `README` con el escenario y las preguntas.

Buenas prácticas antes de tocar nada:

```bash
sha256sum litter.zip suspicious_traffic.pcap   # anotar hashes
unzip -l litter.zip
capinfos suspicious_traffic.pcap
```

## Investigación

### 1. Naturaleza del tráfico

`capinfos` da duración, número de paquetes y protocolos. Con el PCAP abierto en Wireshark, el filtro que ordena el ruido es por volumen y por rareza:

```text
dns.qry.name contains "microsofto365.com"
```

Cientos de consultas `TXT`/`CNAME` largas y de alta entropía hacia un dominio que imita a un servicio legítimo: túnel DNS, no resolución real.

### 2. Identificar la herramienta

La firma del túnel (etiquetas, tamaño de los subdominios, patrón de respuestas) apunta a **dnscat2**. Se confirma decodificando el flujo con el decodificador del proyecto:

```bash
python3 dnscat2-decoder/dnscat2_decoder.py suspicious_traffic.pcap microsofto365.com > dnscat_dump.txt
```

El volcado contiene la sesión reconstruida: comandos, salida y ficheros transferidos. Con eso se responde a la versión del cliente, al nombre que el atacante dio al binario que dejó en el host y al contenido exfiltrado.

### 3. Cuantificar el daño

En el volcado se ve el comando que volcó la base de datos y el total de registros. Ojo con el conteo: el índice arranca en cero, así que el número de filas es el último índice más uno.

## Conclusiones

- Canal: **DNS tunneling** con dnscat2 sobre un dominio de aspecto legítimo.
- Objetivo: datos de clientes (PII) de una base de datos del host de pruebas.
- El host no estaba monitorizado como producción, que es justo lo que lo hizo atractivo.

## Lecciones

- El DNS casi nunca se filtra en el egress: es el canal de exfiltración más cómodo que queda.
- La detección pasa por volumen y entropía por dominio, no por firmas de malware.
- Mitigación: resolver solo a través de resolvers internos, limitar `TXT` y `NULL`, y alertar por consultas por minuto y longitud de etiqueta.
