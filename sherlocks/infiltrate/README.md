---
sherlock: Infiltrate
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, network, pcap, windows, initial-access, lateral-movement]
---

# Infiltrate — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Investigación de una intrusión con evidencia de red y de host. El PCAP identifica el acceso inicial, las credenciales usadas y el movimiento lateral; los logs Windows confirman las sesiones y los procesos. La correlación permite reconstruir el alcance.

## Escenario

La organización detecta conexiones sospechosas hacia un servidor interno. Se entrega un PCAP y una colección de logs y se solicita identificar al atacante, el método de acceso y los hosts afectados.

## Artefactos

- PCAP con tráfico HTTP/SMB/WinRM.
- EVTX de Security/System.
- Logs de aplicación y proxy.
- Listado de sesiones y procesos.

## Metodología

1. Se revisan protocolos y conversaciones en Wireshark/Zeek.
2. Se extraen credenciales, user-agents y rutas HTTP.
3. Se identifican accesos SMB/WinRM y hosts origen/destino.
4. Se cruzan las IPs y cuentas con los EVTX.
5. Se documenta la cadena y los sistemas comprometidos.

```bash
tshark -r capture.pcap -q -z conv,tcp
zeek -r capture.pcap
```

## Preguntas tipo

- ¿Qué servicio se usó para el acceso inicial?
- ¿Qué credenciales se enviaron?
- ¿Qué host actuó como pivote?
- ¿Qué sistemas se accedieron después?
- ¿Qué datos se transfirieron?

## Herramientas

`Wireshark`, `tshark`, `Zeek`, `NetworkMiner`, `EvtxECmd`.

## Evidencia y redacción

Se conservan capturas de conversaciones y eventos con IPs, usuarios y credenciales redactados. No se publican respuestas literales.

## Lecciones aprendidas

- El PCAP revela credenciales y rutas que los logs pueden omitir.
- SMB/WinRM son canales habituales de movimiento lateral.
- La correlación IP/cuenta valida la línea temporal.
- El tráfico cifrado requiere apoyarse en logs de host.

## Detección

- Alertar de SMB/WinRM desde hosts no administrativos.
- Vigilar user-agents y rutas anómalas.
- Correlacionar 4624 tipo 3/10 con flujos de red.
- Revisar transferencias salientes de datos.

## Referencias

- <https://app.hackthebox.com/sherlocks/Infiltrate>
- <https://attack.mitre.org/tactics/TA0008/>
- <https://www.wireshark.org/docs/>
