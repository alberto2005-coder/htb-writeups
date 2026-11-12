---
sherlock: OpTinselTrace-5
domain: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, chainsaw, ransomware, services]
---

# OpTinselTrace-5 — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

Último caso de la saga. Se entrega una colección de logs de eventos Windows de un entorno comprometido; el objetivo es reconstruir la instalación de un servicio malicioso, la propagación y el despliegue de ransomware. Hay decenas de miles de coincidencias Sigma, así que la clave es filtrar y ordenar.

## Evidencias

- Directorio `Logs/` con EVTX de sistema, seguridad, aplicación y PowerShell.
- Reglas Sigma y Chainsaw.
- Eventos de servicio (7045), tareas programadas y procesos.
- Indicadores de cifrado y notas de rescate.

```bash
chainsaw hunt Logs/ -s sigma/ --mapping mappings/ --csv results.csv
```

## Investigación

### 1. Inventario y triaje

Se identifica el host y el rango temporal. Se ejecuta Chainsaw con las reglas Sigma y se agrupa por técnica:

```bash
chainsaw hunt Logs/ -s sigma/ --mapping mappings/ --csv results.csv
cut -d, -f3 results.csv | sort | uniq -c | sort -nr | head
```

Se priorizan 7045 (nuevo servicio), 4697, 4688, 4104 (PowerShell) y 106/2004 (Defender).

### 2. Línea temporal

- Acceso inicial y elevación.
- Instalación de servicio con binario en `ProgramData` o `Temp`.
- Propagación lateral (SMB, WinRM, PsExec).
- Ejecución del ransomware y creación de notas.
- Limpieza de logs o intentos de evasión.

```bash
chainsaw search -t 'Event.System.EventID: =7045' Logs/
```

### 3. Artefacto clave

El evento 7045 aporta `ServiceName`, `ImagePath` y `ServiceType`. La ruta del binario y el usuario que instala el servicio suelen identificar el stage. Los eventos 4688/4104 permiten reconstruir la cadena hasta el cifrado.

```text
7045 -> ImagePath -> proceso -> cifrado/nota
```

## Conclusiones

- El atacante instaló uno o más servicios para ejecutar el ransomware.
- La propagación usó credenciales y herramientas de administración remotas.
- Los logs permiten ordenar servicio, ejecución y cifrado.
- Los IOCs son nombres/rutas de servicio, hashes, cuentas y hosts.

## Lecciones

- 7045 es el evento más directo para servicios maliciosos.
- Chainsaw + Sigma reduce decenas de miles de eventos a una lista manejable.
- La hora del servicio debe compararse con la primera nota de rescate.
- La ausencia de logs de PowerShell no implica que no se ejecutara.

## Referencias

- <https://mwalkowski.com/post/sherlock-optinseltrace-5>
- <https://github.com/WithSecureLabs/chainsaw>
- <https://attack.mitre.org/techniques/T1543/003/>
