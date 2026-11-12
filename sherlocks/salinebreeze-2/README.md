---
sherlock: SalineBreeze-2
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, breach, logs, pcap, lateral-movement]
---

# SalineBreeze-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Investigación de una brecha con múltiples fuentes: logs de acceso, PCAP y eventos de autenticación. Se reconstruye el acceso inicial, la escalada y el movimiento lateral.

## Escenario

Una organización detecta actividad anómala en varios servidores. Se entregan logs y capturas de red para determinar el alcance y las cuentas comprometidas.

## Artefactos

- Access logs y auth logs.
- PCAP de tráfico interno.
- EVTX/Syslog y alertas IDS.
- Listado de cuentas y hosts.

## Metodología

1. Se fija la línea temporal y se identifican picos de tráfico.
2. Se buscan patrones de fuerza bruta, web shells y túneles.
3. Se correlacionan IPs internas con cuentas y procesos.
4. Se revisan SMB/RDP/WinRM para movimiento lateral.
5. Se documentan IOCs y el impacto.

```bash
zeek -r capture.pcap
cat access.log | awk '{print $1}' | sort | uniq -c | sort -nr
```

## Preguntas tipo

- ¿Cuál fue el acceso inicial?
- ¿Qué cuentas se comprometieron?
- ¿Qué hosts se usaron para pivotar?
- ¿Qué datos salieron?
- ¿Qué IOC permite detectar la campaña?

## Herramientas

`Zeek`, `Wireshark`, `grep/awk`, `EvtxECmd`, `Timeline Explorer`.

## Evidencia y redacción

Se conservan capturas de flujos y hashes con IPs, usuarios y dominios redactados.

## Lecciones aprendidas

- La correlación de logs y PCAP acota el alcance.
- Los túneles dejan patrones de flujo reconocibles.
- El movimiento lateral usa credenciales válidas.
- Un IOC aislado no explica la cadena.

## Detección

- Alertar de fuerza bruta seguida de éxito.
- Vigilar web shells y procesos de servidor.
- Detectar SMB/RDP internos inusuales.
- Correlacionar DNS y conexiones salientes.

## Referencias

- <https://app.hackthebox.com/sherlocks/SalineBreeze-2>
- <https://attack.mitre.org/techniques/T1021/>
- <https://docs.zeek.org/>
