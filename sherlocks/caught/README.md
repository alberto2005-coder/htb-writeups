---
sherlock: Caught
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, jscript, sliver, gpo, wmi]
---

# Caught — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una amenaza interna utiliza Active Directory para moverse y mantener acceso. Se pide reconstruir la cadena desde la ejecución de JScript hasta la persistencia con WMI y el abuso de GPO.

## Evidencias

- Registros de Seguridad, PowerShell y Sysmon.
- Objetos de AD y cambios de ACL.
- Scripts JScript y artefactos de deserialización.
- Eventos de GPO y de consumidores WMI.
- Telemetría de red compatible con Sliver.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigación

### 1. Ejecución inicial

Se identifican `wscript`/`cscript`, líneas de comandos y scripts en rutas de usuario. La deserialización JScript puede ejecutar código sin un binario convencional; se revisan los objetos creados y el proceso padre.

```powershell
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational'; ID=4104}
```

### 2. Movimiento y permisos

Los cambios de ACL se correlacionan con la cadena `GenericAll` → `GenericWrite` → abuso de GPO. Se documenta qué objeto obtuvo control, sobre cuál y en qué momento.

- Usuario o grupo modificado.
- Derecho concedido.
- GPO enlazada y equipo afectado.
- Cambio de contraseña o de grupo.

### 3. Persistencia y C2

Se revisan consumidores de eventos WMI, tareas programadas y servicios. Los eventos de red y los artefactos de memoria o disco se comparan con el perfil de Sliver: beacon, sesiones y tareas.

```powershell
Get-WmiObject -Namespace root\subscription -Class __EventConsumer
Get-WmiObject -Namespace root\subscription -Class __EventFilter
```

## Conclusiones

- Script y usuario que iniciaron la cadena.
- Ruta de privilegios en AD y GPO abusada.
- Persistencia WMI y evidencia de C2.
- IOCs: rutas, cuentas, GUID y hashes, redactados.

## Lecciones

- Un cambio de ACL aparentemente menor puede habilitar un GPO completo.
- Los consumidores WMI son persistencia silenciosa y persistente.
- La deserialización JScript requiere revisar scripts, no solo ejecutables.

## Referencias

- <https://www.hackthebox.com/sherlocks/Caught>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://attack.mitre.org/techniques/T1546/003/>
- <https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-wmi-events>
