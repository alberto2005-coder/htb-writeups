---
sherlock: SalineBreeze-1
category: Threat Intelligence
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, salt-typhoon, mitre-attack, rootkit, telecom]
---

# SalineBreeze-1 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un analista junior recibe la tarea de investigar Salt Typhoon y una campaña de espionaje contra redes de telecomunicaciones. Debe identificar el actor, su malware, las vulnerabilidades que explota y las técnicas de MITRE ATT&CK asociadas.

## Evidencias

- Ficha de MITRE ATT&CK del grupo.
- Informes de proveedores sobre implants Linux y rootkits.
- Avisos gubernamentales sobre telecomunicaciones.
- No hay binarios ni PCAP: la investigación es OSINT.

```text
Punto de partida: ficha MITRE del grupo y advisories de CISA/NSA.
```

## Investigación

### 1. Inventario y triaje

Se identifican los alias del actor y su objetivo. Salt Typhoon se asocia a espionaje de estado y a infraestructura de telecomunicaciones; las campañas documentadas incluyen acceso a routers, switches y sistemas de gestión.

- Actor vinculado a China.
- Objetivo: redes de telecomunicaciones e infraestructura crítica.
- Técnicas de acceso inicial: credenciales válidas, dispositivos de borde y vulnerabilidades de aplicaciones expuestas.

### 2. Malware y rootkits

Los informes públicos describen un implant Linux para equipos de red que captura tráfico y borra registros. En campañas relacionadas aparece `Demodex`, un rootkit de modo kernel que oculta procesos y archivos.

- `JumbledPath` se asocia a la recolección y al borrado de evidencia.
- `Demodex` se instala tras el acceso y manipula el kernel para ocultar actividad.
- La persistencia puede sobrevivir a reinicios mediante servicios o módulos.

### 3. Mapeo MITRE

Se relacionan las técnicas observadas con ATT&CK:

- `T1190` — Exploit Public-Facing Application.
- `T1078` — Valid Accounts.
- `T1014` — Rootkit.
- `T1070.002` — Indicator Removal: Clear Linux or Mac System Logs.
- `T1040` — Network Sniffing.

## Conclusiones

- Salt Typhoon combina acceso a dispositivos de borde con implants sigilosos.
- El rootkit dificulta la detección con herramientas del sistema; se necesita telemetría externa.
- La respuesta debe incluir aislamiento, reimagen y rotación de credenciales.
- Los aliases y las herramientas cambian; el mapeo de TTP es la parte reutilizable.

## Lecciones

- La inteligencia sobre APT debe alimentar reglas de detección y planes de respuesta.
- Un rootkit puede ocultar procesos, pero no todo el tráfico de red.
- En telecomunicaciones, la cadena de suministro y los dispositivos de borde son críticos.

## Referencias

- <https://www.hackthebox.com/sherlocks/SalineBreeze-1>
- <https://attack.mitre.org/groups/G1045/>
- <https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-038a>
- <https://attack.mitre.org/techniques/T1014/>
