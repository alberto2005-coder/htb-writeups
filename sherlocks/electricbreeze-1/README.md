---
sherlock: ElectricBreeze-1
category: Threat Intelligence
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, mitre-attack, volt-typhoon, apt, osint]
---

# ElectricBreeze-1 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un equipo de seguridad quiere evaluar la exposición a Volt Typhoon. Como analista junior de threat intelligence, se pide investigar el grupo, mapear sus tácticas y técnicas con MITRE ATT&CK y explicar qué técnicas de credenciales y persistencia son relevantes para una organización.

## Evidencias

- Ficha pública del grupo en MITRE ATT&CK.
- Avisos de CISA y de agencias aliadas sobre Volt Typhoon.
- Informes de proveedores sobre la explotación de dispositivos de borde.
- No se entrega malware ni captura: la evidencia es OSINT.

```text
Fuente primaria: https://attack.mitre.org/groups/G1017/
```

## Investigación

### 1. Inventario y triaje

Se empieza por la ficha de MITRE, que resume el actor, sus alias y las técnicas observadas. Se anotan las fechas de actividad, los sectores objetivo y las técnicas con mayor valor para la organización.

- Grupo tracked como Volt Typhoon / Vanguard Panda / BRONZE SILENCE.
- Activo desde al menos 2021.
- Objetivo principal: infraestructura crítica y redes de telecomunicaciones.
- Técnicas de acceso inicial ligadas a dispositivos de borde y credenciales válidas.

### 2. Credenciales y Active Directory

MITRE lista dos sub-técnicas de `T1003` para el grupo: LSASS Memory (`T1003.001`) y NTDS (`T1003.003`). La segunda afecta a la base de datos de Active Directory, `ntds.dit`.

Para descifrar `ntds.dit` se necesita la colmena `SYSTEM`, que contiene la bootkey. Sin ella, el archivo no se puede descifrar de forma práctica.

```text
T1003.003 → NTDS → Active Directory → SYSTEM hive
```

### 3. Explotación de borde y persistencia

Los informes públicos describen la explotación de un zero-day en Versa Director en 2024 (CVE-2024-39717) y el uso de credenciales válidas para moverse por la red. La persistencia se apoya en cuentas locales, servicios y tareas del sistema, no en malware llamativo.

- `T1190` — Exploit Public-Facing Application.
- `T1078` — Valid Accounts.
- `T1053` — Scheduled Task/Job.
- `T1562.001` — Impair Defenses: Disable or Modify Tools.

## Conclusiones

- Volt Typhoon prioriza el sigilo y el uso de credenciales válidas.
- La extracción de NTDS y el abuso de cuentas de servicio son riesgos directos.
- La defensa debe cubrir dispositivos de borde, segmentación, MFA y monitorización de cuentas privilegiadas.
- Los IOC de infraestructura cambian con rapidez; las TTP son más estables.

## Lecciones

- La inteligencia de amenazas debe traducirse en detecciones y controles, no solo en una lista de IOCs.
- MITRE ATT&CK es útil para comparar cobertura, pero no sustituye la evidencia local.
- Un actor de estado-nación puede operar durante meses con herramientas del sistema.

## Referencias

- <https://www.hackthebox.com/sherlocks/ElectricBreeze-1>
- <https://attack.mitre.org/groups/G1017/>
- <https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-038a>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-39717>
