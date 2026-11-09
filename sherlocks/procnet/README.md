---
sherlock: ProcNet
domain: DFIR / Red y endpoint
difficulty: Hard
platform: Hack The Box
evidence: PCAP, API Monitor y Sysmon de un DC y de un puesto
tools: [Wireshark, API Monitor, EvtxECmd, Timeline Explorer]
---

# ProcNet — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El equipo rojo simula un **framework de C2** de código abierto y entrega lo capturado durante el ejercicio: tráfico, llamadas a la API de Windows y Sysmon, tanto del controlador de dominio como del puesto del empleado comprometido. El objetivo es reconstruir la cadena con evidencia de endpoint, no sólo de red.

## Evidencia

- Dos directorios: `DC` y `Employee`, cada uno con `pcapng`, una captura de **API Monitor** (`.apmx64`) y logs de Sysmon.

## Método

1. **Qué procesos hablan**: del PCAP a Sysmon, identificar el binario que abre la conexión y su padre.

```bash
tshark -r emp.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.dst -e tcp.dstport | sort -u
```

```text
EventID 3 (Sysmon) | Image, DestinationIp, DestinationPort
```

2. **Inyección y módulos**: en Sysmon (EventID 7, *ImageLoad*) se ve qué DLL carga un proceso que no debería (por ejemplo un ejecutable de juego cargando una librería de gestión remota).

3. **API Monitor**: la captura `.apmx64` muestra las llamadas reales del proceso. Ahí se confirma el uso de **WMI** (`ExecQueryWmi`, conexiones a `root\cimv2`) y de funciones de sistema como `GetFullPathNameW` al preparar la descarga.

4. **De empleado a DC**: comparar las dos capturas; el movimiento lateral se ve en el mismo binario/DLL ejecutándose en el otro host y en las llamadas WMI remotas.

5. **Cronología**: unir Sysmon de ambos hosts por hora y marcar primer *beacon*, ejecución remota y recolección.

## Qué enseña

- La red dice *qué* salió; el endpoint dice *quién* lo hizo: correlacionar ambos es obligatorio.
- API Monitor convierte un binario opaco en una lista de llamadas: se ve la intención aunque el malware esté empaquetado.
- Una DLL de administración remota cargada por un proceso que no la necesita es una firma de movimiento lateral.

## Tropiezos

- **Nombres legítimos**: el proceso puede llamarse como un juego o una herramienta común; la anomalía está en sus módulos.
- **Volumen de Sysmon**: filtrar por `Image` y por ventana temporal antes de leer.
- **API Monitor y arquitectura**: una captura de 64 bits no muestra llamadas de un proceso de 32 bits.
