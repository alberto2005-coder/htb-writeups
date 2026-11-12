---
sherlock: Lit
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, rdp, brute-force, evtx, logon]
---

# Lit — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Un servidor Windows sufre fuerza bruta contra RDP. Se analizan eventos 4625/4624/4776 y el `Security.evtx` para identificar origen, cuentas probadas y el inicio de sesión exitoso.

## Escenario

El equipo de seguridad recibe alertas de múltiples fallos de autenticación en un host. Se entrega el log de seguridad y se pide determinar si hubo acceso y desde dónde.

## Artefactos

- `Security.evtx`.
- `Microsoft-Windows-TerminalServices-LocalSessionManager/Operational.evtx`.
- `Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational.evtx`.
- Firewall y logs de red.

## Metodología

1. Se filtran 4625 por `Logon Type 3/10` y se agrupan por IP y cuenta.
2. Se identifica el patrón de fuerza bruta y el primer 4624 exitoso.
3. Se revisan 4776/4648 para autenticación NTLM/explicit.
4. Se confirma la sesión RDP con los logs de TerminalServices.
5. Se documenta la cuenta comprometida y el origen.

```bash
EvtxECmd.exe -f Security.evtx --csv C:\\Evidence\\out
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625}
```

## Preguntas tipo

- ¿Desde qué IP se originó la fuerza bruta?
- ¿Qué cuentas se probaron?
- ¿Hubo un login exitoso? ¿Cuándo?
- ¿Qué tipo de logon se usó?
- ¿Se creó una sesión RDP persistente?

## Herramientas

`EvtxECmd`, `Timeline Explorer`, `Event Viewer`, `RDP log parser`.

## Evidencia y redacción

Se conservan capturas de los eventos con IPs, usuarios y dominios redactados.

## Lecciones aprendidas

- 4625 aislado no es ataque; el patrón sí.
- 4624 con Logon Type 10 confirma RDP.
- Los logs de TerminalServices complementan Security.
- La hora del primer éxito marca el inicio de la investigación.

## Detección

- Alertar de múltiples 4625 seguidos de 4624.
- Limitar RDP expuesto y aplicar MFA.
- Bloquear IPs tras umbral de fallos.
- Vigilar cuentas válidas usadas desde ubicaciones nuevas.

## Referencias

- <https://app.hackthebox.com/sherlocks/Lit>
- <https://attack.mitre.org/techniques/T1110/001/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625>
