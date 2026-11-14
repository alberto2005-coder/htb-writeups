---
topic: Mapeo con MITRE ATT&CK
tags: [threat-hunting, mitre, attck, detection, ttps, coverage]
---

# Mapeo con MITRE ATT&CK

[🌐 English](mitre-attack-mapping.en.md) | **Español**

## Concept

MITRE ATT&CK es una base de tácticas y técnicas observadas en ataques reales. Mapear una ficha, un incidente o una regla de detección a ATT&CK permite comparar cobertura, priorizar telemetría y comunicar el comportamiento del adversario con un lenguaje común.

## Cuándo aplica

- Análisis de un actor o de una campaña.
- Diseño de detecciones y reglas SIEM.
- Evaluación de brechas de telemetría.
- Informes de threat intelligence y DFIR.

## Procedimiento

1. Describir el comportamiento observable, no la herramienta.
2. Buscar la táctica y la técnica correspondiente.
3. Anotar la sub-técnica y la fuente de datos.
4. Verificar si la organización tiene telemetría para detectarla.
5. Registrar la cobertura y las limitaciones.

```text
Acción: borrado de logs de Linux
Táctica: Defense Evasion (TA0005)
Técnica: Indicator Removal (T1070)
Sub-técnica: Clear Linux or Mac System Logs (T1070.002)
```

## Variantes

- Mapeo de un grupo (Gxxxx) y sus técnicas.
- Mapeo de software (Sxxxx) a técnicas.
- Mapeo inverso: de una regla a las técnicas que cubre.
- Uso de ATT&CK Navigator para capas de cobertura.
- Mapeo de procedencia a datos de telemetría.

## Limitaciones

- ATT&CK describe comportamiento, no una lista de IOC.
- Una técnica puede tener varias implementaciones.
- El mapeo puede ser ambiguo sin contexto.
- La cobertura de una regla no garantiza detección real.

## Mitigación y detección

- Validar cada regla con datos reales y pruebas controladas.
- Priorizar técnicas usadas por actores relevantes.
- Documentar la fuente de datos y el supuesto.
- Revisar la cobertura periódicamente y tras cambios de infraestructura.

## Referencias

- <https://attack.mitre.org/>
- <https://mitre-attack.github.io/attack-navigator/>
- <https://attack.mitre.org/resources/attack-data-and-tools/>
- <https://www.cisa.gov/cyber-threat-intelligence>
