---
sherlock: UFO-1
category: Threat Intelligence
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, mitre, sandworm, apt44, ics]
---

# UFO-1 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un analista de un sector ICS debe estudiar Sandworm Team (APT44) con MITRE ATT&CK. No hay artefactos: la evidencia es la documentación pública y la capacidad de mapear campañas a técnicas.

## Evidencias

- No se entrega ZIP ni artefactos.
- Se trabaja con MITRE ATT&CK, CISA y fuentes públicas.
- La respuesta se apoya en el grupo G0034 y sus campañas.

```text
Grupo: Sandworm Team (G0034), también BlackEnergy/APT44
Campaña clave: 2016 Ukraine Electric Power Attack (C0015)
```

## Investigación

### 1. Inventario y triaje

Se identifica el grupo y se listan sus campañas documentadas. Se separan las técnicas de acceso inicial, las de impacto físico y las de evasión.

### 2. Línea temporal

Se ordenan los hitos:
- 2009: inicios documentados.
- 2015/2016: campaña contra la red eléctrica ucraniana.
- 2017: NotPetya.
- 2022: Industroyer2 y ataques a infraestructura.

### 3. Artefacto clave

El artefacto es la página de ATT&CK del grupo y su capa de Navigator. Se anotan las técnicas con ID y se comprueba si cada una tiene una fuente citada.

```bash
# Navigator: cargar G0034 y exportar la capa
```

## Conclusiones

- Sandworm es un actor de Estado con foco en infraestructura crítica.
- Sus campañas combinan acceso remoto, malware modular e impacto destructivo.
- El mapeo a ATT&CK permite priorizar telemetría ICS/IT.
- La atribución se basa en fuentes oficiales, no en un único IOC.

## Lecciones

- La inteligencia de amenazas también se hace sin malware.
- Las técnicas ICS requieren contexto físico.
- Documentar la fuente evita sobreatribuir.

## Referencias

- <https://www.hackthebox.com/sherlocks/UFO-1>
- <https://attack.mitre.org/groups/G0034/>
- <https://attack.mitre.org/campaigns/C0015/>
