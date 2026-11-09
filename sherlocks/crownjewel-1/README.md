---
sherlock: CrownJewel-1
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, ntds, vss, credential-dumping, mft]
---


# CrownJewel-1 — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Forela es una empresa que sospecha un compromiso de su Active Directory. El equipo de respuesta entrega una imagen del controlador de dominio y los artefactos de los hosts implicados. El objetivo es reconstruir qué hizo el intruso, cómo obtuvo las credenciales del dominio y qué evidencia lo demuestra.

## Evidencias

- `$MFT` del volumen del DC, con marcas de tiempo `$SI` y `$FN`.
- `NTFS.evtx` (registro del sistema de ficheros) y `SECURITY.evtx` / `SYSTEM.evtx`.
- Copia del directorio `NTDS` y del hive `SYSTEM`, si el atacante llegó a extraerlos.

## Investigación

### 1. Creación de una copia de sombra

El primer indicio es la ejecución de utilidades de instantáneas de volumen en el DC:

```powershell
vssadmin create shadow /for=C:
# o alternativas equivalentes
diskshadow.exe
wmic shadowcopy call create Volume='C:\'
```

En `SECURITY.evtx`/`SYSTEM.evtx` se busca el servicio `VSS` (`vssvc.exe`) y, si hay auditoría de procesos, el `4688` con `vssadmin.exe` o `diskshadow.exe` como línea de comandos.

### 2. Extracción de NTDS.dit

Desde la copia de sombra se accede a `C:\Windows\NTDS\ntds.dit`, la base de datos del directorio, y se copia junto con el hive `SYSTEM` (necesario para la clave de arranque). El `$MFT` permite situar la creación y la copia: se comparan `$SI` (cambios de contenido) con `$FN` (metadatos del nombre) para detectar timestomping.

```bash
# análisis del $MFT con las herramientas del caso
MFTECmd.exe -f '$MFT' --csv out/
```

### 3. Qué se llevó el atacante

La pareja `ntds.dit` + `SYSTEM` permite extraer todos los hashes del dominio con `secretsdump`/`impacket` y obtener `krbtgt`, lo que habilita persistencia con golden ticket. La evidencia clave es la **copia** de ambos ficheros, no un `4662` de replicación: aquí no hubo DCSync, hubo robo del fichero.

## Conclusiones

- El control del dominio se obtuvo copiando `NTDS.dit` y el hive `SYSTEM` desde una instantánea de volumen creada con `vssadmin`/`diskshadow`, no mediante replicación de directorio.
- Con `krbtgt` en manos del atacante, la rotación doble de la cuenta es obligatoria aunque no se observe un golden ticket en los logs.
- El alcance es todo el dominio: cualquier cuenta y equipo queda comprometido.

## Lecciones

- Crear una copia de sombra en un DC es un paso de reconocimiento/exfiltración, no una tarea administrativa rutinaria: `vssadmin` y `diskshadow` deben alertar.
- `ntds.dit` + `SYSTEM` es equivalente a un DCSync: el impacto se mide por el fichero, no solo por el evento `4662`.
- El `$MFT` demuestra la copia y desmonta el timestomping comparando `$SI` con `$FN`.
- La respuesta empieza por aislar el DC, rotar `krbtgt` dos veces y revisar cuentas con privilegios.

## Referencias

- [MITRE T1003.003 — OS Credential Dumping: NTDS](https://attack.mitre.org/techniques/T1003/003/)
- [Microsoft Learn — vssadmin](https://learn.microsoft.com/windows-server/administration/windows-commands/vssadmin)
