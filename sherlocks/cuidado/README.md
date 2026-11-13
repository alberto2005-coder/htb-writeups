---
sherlock: Cuidado
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, cryptominer, upx, bash, c2]
---

# Cuidado — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

El SOC detecta consumo anómalo de CPU y conexiones salientes desde un servidor Linux. Se entrega una captura PCAP para identificar la descarga, el dropper y el minero que se está ejecutando.

## Evidencias

- Captura PCAP del tráfico del servidor.
- Descarga HTTP identificada en la captura.
- Script de shell y binario empaquetado con UPX.
- Indicadores de C2 y del pool de minería.

```bash
capinfos capture.pcap
tshark -r capture.pcap -Y 'http.request' -T fields -e frame.time -e ip.src -e http.host -e http.request.uri
```

## Investigación

### 1. Inventario y triaje

Se obtiene el rango temporal, los interlocutores y los protocolos. Las descargas HTTP y las conexiones a puertos altos suelen explicar el inicio.

```bash
tshark -r capture.pcap -q -z endpoints,ip
tshark -r capture.pcap -Y 'tcp.port == 80 || tcp.port == 443' -T fields -e http.host -e tls.handshake.extensions_server_name
```

### 2. Línea temporal

- Primera conexión al servidor de descarga.
- Ejecución del script y descarga del binario.
- Inicio de conexiones periódicas al pool.
- Persistencia mediante cron o servicio.

La marca temporal del PCAP se contrasta con la de los archivos del dropper.

### 3. Artefacto clave

El script de shell descarga un binario comprimido con UPX y lo ejecuta. Al descomprimir con `upx -d`, se identifican cadenas del minero, la wallet y el dominio del pool.

```bash
upx -d miner.bin -o miner.unpacked
strings -a miner.unpacked | grep -Ei 'pool|wallet|xmrig|stratum'
```

## Conclusiones

- El acceso inicial descargó un dropper desde HTTP.
- El dropper ejecutó un minero ofuscado con UPX.
- El tráfico periódico corresponde a Stratum o al pool identificado.
- IOCs: URL, hash, dominio y puerto, redactados.

## Lecciones

- El tráfico de minería puede parecer HTTPS legítimo si no se revisa el SNI.
- UPX sigue siendo una capa de ofuscación común.
- La persistencia debe buscarse aunque el proceso ya no esté activo.

## Referencias

- <https://www.hackthebox.com/sherlocks/Cuidado>
- <https://upx.github.io/>
- <https://attack.mitre.org/techniques/T1496/>
