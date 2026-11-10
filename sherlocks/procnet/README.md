---
sherlock: ProcNet
domain: DFIR / Red team y endpoint
difficulty: Hard
platform: Hack The Box
evidence: PCAP, API Monitor y Sysmon de un DC y de un puesto
tools: [Wireshark, API Monitor, EvtxECmd, Timeline Explorer]
state: Retired
tags: [dfir, c2, sysmon, api-monitor, ja3, lateral-movement]
---

# ProcNet — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

El equipo rojo simula un **framework de C2 de código abierto** y entrega lo capturado durante el ejercicio: tráfico, llamadas a la API de Windows y Sysmon, tanto del controlador de dominio como del puesto del empleado comprometido. El objetivo es reconstruir la cadena con evidencia de endpoint, no sólo de red.

## Evidencias

```text
DC/         pcapng + apmx64 (API Monitor) + Sysmon .evtx
Employee/   pcapng + apmx64 (API Monitor) + Sysmon .evtx
```

## Investigación

### 1. Empezar por el empleado

El enunciado dice que el puesto fue el primero. En su `pcapng`, `Statistics → Conversations` deja dos IPs intercambiando miles de paquetes; el resto es ruido de fondo.

```bash
tshark -r Employee.pcapng -q -z conv,tcp
tshark -r Employee.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e ip.dst -e tcp.dstport | sort -u
```

### 2. Identificar el implante y el framework

Sysmon **EventID 1** (creación de proceso) y **EventID 3** (conexión de red) unen binario y destino. Para el framework, el dato que lo distingue es el **fingerprint JA3** del cliente TLS: cada librería C2 negocia con una huella concreta.

```bash
tshark -r Employee.pcapng -Y 'tls.handshake.type==1' \
  -T fields -e ip.dst -e tls.handshake.ja3 | sort -u
```

Con el JA3 y el patrón de *beacon* (intervalo regular, mismo tamaño de petición) se identifica la familia del framework y se confirma con la telemetría del endpoint.

### 3. API Monitor: la intención

El `.apmx64` muestra las llamadas reales del proceso, aunque el binario esté empaquetado. Aquí lo revelador es la **enumeración de credenciales**: las llamadas de la API de Windows Vault (enumerar *vaults*, leer *items*) aparecen en el proceso del atacante, no en una herramienta de administración.

```text
API Monitor → filter: VaultEnumerateVaults, VaultEnumerateItems, CryptUnprotectData
```

Eso convierte la hipótesis «C2» en «C2 con robo de credenciales», que explica el salto al DC.

### 4. Del empleado al DC

Se repite el ejercicio con `DC/pcapng`: mismo binario o DLL en el otro host, mismas llamadas, y eventos de Sysmon **7 (ImageLoad)** mostrando una librería de administración remota cargada por un proceso que no la necesita (por ejemplo, un binario con nombre de juego).

### 5. Cronología

Unir los Sysmon de ambos hosts por hora UTC: primer *beacon* en el empleado, ejecución de la enumeración de vaults, aparición del implante en el DC y recolección posterior. Marcar el intervalo entre beacons da la periodicidad del C2.

## Conclusiones

- El framework se identifica por **JA3 + cadencia de beacon**, no por el nombre del proceso.
- La API Monitor demuestra **acceso a credenciales** desde el implante, el puente hacia el controlador de dominio.
- La cadena se sostiene con dos fuentes: red (a dónde) y endpoint (quién y con qué llamadas).

## Lecciones

- En un ejercicio de red team, la pregunta no es «¿hay C2?» sino «¿qué hizo el C2 en el host?».
- JA3 sobrevive al cifrado y agrupa miles de flujos en una huella; es el mejor atajo cuando el payload es opaco.
- API Monitor convierte un binario opaco en una lista de intenciones; Vault es credenciales, no «actividad rara».
- Filtrar Sysmon por `Image` y ventana temporal antes de leer: el volumen es el enemigo.
- Una captura de 64 bits no muestra llamadas de un proceso de 32 bits: comprobar la arquitectura antes de concluir «no hay nada».
