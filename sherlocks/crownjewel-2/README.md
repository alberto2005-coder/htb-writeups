---
title: CrownJewel-2
category: DFIR / Active Directory
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, ntds, ntdsutil, esent, evtx]
sherlock: CrownJewel-2
domain: DFIR
---

# CrownJewel-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

## Escenario

Segunda vuelta del compromiso del DC de Forela. En CrownJewel-1 el atacante copió `NTDS.dit` con **`vssadmin`**; aquí vuelve con una cuenta de administrador de dominio y esta vez usa **`ntdsutil.exe`**, que también crea una instantánea de volumen pero deja rastro en el log **Application** de la base ESE (ESENT).

## Evidencias

- Carpeta `Artifacts/` con `Application.evtx`, `Security.evtx`, `System.evtx` y el log operacional de NTFS.
- `EvtxECmd` para pasar los EVTX a CSV, `Timeline Explorer` o `Hayabusa` para filtrar.
- Las horas se piden en UTC y con formato `YYYY-MM-DD HH:MM:SS`.

## Investigación

### 1. La instantánea

`ntdsutil` dispara el servicio de instantáneas antes de copiar. En `System.evtx`, el servicio **Volume Shadow Copy** pasa a `running` (evento 7036); esa marca es el inicio del volcado y lo que se pregunta primero.

```bash
EvtxECmd.exe -f System.evtx --csv out --csvf system.csv
grep -i "Volume Shadow Copy" out/system.csv
```

### 2. ESE: los tres eventos que delatan la copia

La base ESE registra en **Application**:

- **325** — se va a crear una copia nueva de la base (incluye la ruta de destino),
- **326** — copia creada,
- **327** — base desmontada y lista para usar.

Esa secuencia es la prueba de que se usó `ntdsutil` y no `vssadmin`, y da la **ruta completa** del `ntds.dit` volcado.

### 3. Quién y con qué

En `Security.evtx`: `4624` del administrador de dominio comprometido, `4672` (privilegios especiales) para el mismo `Logon ID` y `4688` con `ntdsutil.exe`. El `Logon ID` es lo que une los tres eventos; con él se identifica al usuario y el host de origen.

Además, `ntdsutil` enumera grupos durante la operación: aparecen consultas a **Backup Operators** y **Administrators**, útiles para confirmar el objetivo.

### 4. Salida de los datos

La copia se saca del DC por SMB: `5140`/`5145` sobre `C$` o `ADMIN$`, o directamente hacia un recurso del atacante. Cruzar la hora de los `325/326` con esos accesos cierra la línea temporal.

## Conclusiones

El volcado se hizo con `ntdsutil`, no con `vssadmin`: la firma es la terna **7036 (VSS) + 325/326/327 (ESE) + 4688**, y la ruta del fichero sale del propio evento 325. La cuenta usada es de administrador de dominio, así que hay que rotar `krbtgt` dos veces y revisar la persistencia que dejó.

## Lecciones

- `ntdsutil` deja triple rastro (servicio VSS, eventos ESENT y proceso); `vssadmin` solo deja el servicio y el binario.
- El `Logon ID` une `4624` → `4688` → `4672`; sin él, los eventos no cuentan una historia.
- El evento 325 da la ruta exacta del volcado: no hay que adivinarla por el `$MFT`.

## Mitigaciones y detección

- Restringir `ntdsutil.exe` y `vssadmin.exe` con AppLocker/WDAC y alertar de su ejecución en un DC.
- Cuentas de administrador de dominio en *tiering*, `Protected Users` y LAPS.
- Alertas: `7036` de VSS seguido de `325/326/327` en menos de 10 minutos; `5145` sobre `C$`/`ADMIN$` desde hosts que no son de administración.
- MITRE: T1003.003, T1021.002, T1078.
