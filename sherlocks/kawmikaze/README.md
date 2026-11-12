---
sherlock: Kawmikaze
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, loader, process-injection, c2, evasion]
---

# Kawmikaze — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni IOC reales.

## TL;DR

Un loader ofuscado inyecta un payload en un proceso legítimo y contacta con un C2. Se combinan análisis estático, memoria y red para identificar la cadena y la persistencia.

## Escenario

Un endpoint genera tráfico cifrado hacia un destino desconocido y muestra procesos hijos inusuales. Se entrega una muestra y un volcado de memoria.

## Artefactos

- Binario PE, secciones y recursos.
- Memoria del proceso sospechoso.
- PCAP/TLS y logs de proxy.
- Claves `Run`, tareas y servicios.

## Metodología

1. Se identifican empaquetador/ofuscación con DIE y `capa`.
2. Se revisan imports y cadenas para APIs de inyección.
3. En memoria se buscan regiones ejecutables sin respaldo.
4. Se correlaciona el proceso inyectado con conexiones.
5. Se extrae el payload y se documentan IOCs.

```bash
capa -vv sample.exe
vol.py -f mem.raw malfind
vol.py -f mem.raw netscan
```

## Preguntas tipo

- ¿Qué técnica de inyección usa?
- ¿Qué proceso es el objetivo?
- ¿Cuál es el C2 y el protocolo?
- ¿Cómo persiste tras el reinicio?
- ¿Qué payload final se ejecuta?

## Herramientas

`CAPA`, `Detect It Easy`, `Volatility`, `Procmon`, `Wireshark`.

## Evidencia y redacción

Se conservan hashes, regiones de memoria y conexiones con IPs/dominios redactados.

## Lecciones aprendidas

- La inyección deja regiones sin archivo de respaldo.
- El proceso legítimo oculta la ejecución.
- TLS no impide correlacionar destino y proceso.
- La persistencia puede ser independiente del loader.

## Detección

- Alertar de `CreateRemoteThread`/`QueueUserAPC` inusuales.
- Monitorizar procesos con regiones RWX.
- Correlacionar conexiones de procesos no esperados.
- Aplicar YARA en memoria.

## Referencias

- <https://app.hackthebox.com/sherlocks/Kawmikaze>
- <https://attack.mitre.org/techniques/T1055/>
- <https://github.com/mandiant/capa>
