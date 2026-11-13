---
sherlock: Zenith
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, phishing, evtx, persistence, privilege-escalation]
---

# Zenith — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un correo con un adjunto malicioso inicia una intrusión en un equipo Windows. Se pide identificar la ejecución inicial, la persistencia y la escalada de privilegios a partir de los eventos del sistema.

## Evidencias

- Mensaje de correo y adjunto.
- Registros EVTX de Seguridad, Sistema y PowerShell.
- Prefetch y árbol de procesos.
- Tareas programadas y claves de persistencia.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigación

### 1. Correo y ejecución inicial

Se revisan cabeceras, adjunto y nombre del archivo. El evento de creación de proceso muestra el padre real: Outlook, un compresor o el Explorador. Esa relación distingue una ejecución por phishing de una ejecución manual.

```bash
EvtxECmd.exe -d Logs --csv out --csvf evtx.csv
```

### 2. Persistencia

Se buscan claves `Run`, tareas programadas y servicios creados después del primer acceso. La hora del evento se compara con la del archivo y con el prefetch.

- Nombre de la tarea o servicio.
- Usuario que la creó.
- Binario o script asociado.
- Primera y última ejecución.

### 3. Escalada de privilegios

Los eventos 4672, 4688 y los registros de PowerShell permiten reconstruir qué cuenta obtuvo privilegios y con qué herramienta. Se revisan también accesos a `lsass` y cambios de grupo local.

## Conclusiones

- Vector inicial y archivo ejecutado.
- Mecanismo de persistencia y cuenta utilizada.
- Evidencia de escalada.
- IOCs: rutas, nombres y hashes, redactados.

## Lecciones

- El proceso padre es más fiable que el nombre del ejecutable.
- Una tarea programada puede pasar desapercibida si solo se revisan claves `Run`.
- Los eventos de PowerShell deben correlacionarse con el árbol de procesos.

## Referencias

- <https://www.hackthebox.com/sherlocks/Zenith>
- <https://attack.mitre.org/techniques/T1566/001/>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688>
