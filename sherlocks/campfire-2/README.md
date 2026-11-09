---
title: Campfire-2
category: DFIR / Active Directory
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, asrep, kerberos, evtx]
---

# Campfire-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

## Escenario

Segunda parte de Campfire: tras el robo de un ticket en la primera, el atacante consigue una cuenta y busca más credenciales. La evidencia vuelve a ser un conjunto de logs de eventos de un dominio pequeño; el foco está en **AS-REP roasting** y en el uso posterior de la cuenta.

## Evidencia y preparación

```bash
EvtxECmd.exe -d . --csv out --csvf evtx.csv
```

Canales: `Security.evtx`, `System.evtx` y `Microsoft-Windows-PowerShell/Operational`.

## Método

- **4768** con `PreAuthType = 0` (sin preautenticación) es la firma de AS-REP: el DC devuelve un blob cifrado con la contraseña del usuario.
- Agrupar 4768 por `TargetUserName` y hora; una cuenta que recibe muchos en segundos está siendo enumerada o *roasted*.
- Buscar después **4624 tipo 3/10** de esa misma cuenta en hosts donde no suele entrar, y **4769** para ver qué servicios pidió.
- En PowerShell, **4104** puede contener el comando que generó el ticket (Rubeus, `GetNPUsers`, `Invoke-Kerberoast`).
- Cruzar con el log del servicio KDC si está disponible: el `TicketOptions` y el `Status` distinguen éxito de fallo.

## Hallazgos (patrón)

```text
4768  user=<cuenta>  PreAuthType=0  Status=0x0
4624  type=3  user=<cuenta>  src=<host atacante>
4769  service=<SPN>  enc=0x17
```

La secuencia 4768 sin preauth → 4624 en un host nuevo → 4769 RC4 describe el robo de credenciales y su uso.

## Lecciones

- El AS-REP no requiere autenticación: cualquier usuario puede lanzarlo y el DC lo registra igual.
- Una cuenta sin preautenticación es una debilidad de configuración, no un fallo de contraseña.
- El cifrado RC4 en 4769 sigue siendo el indicador más fiable de Kerberoasting.

## Detección y mitigación

- Alertar de 4768 con `PreAuthType=0` fuera de horario o en volumen.
- Activar preautenticación en todas las cuentas y usar contraseñas largas en las de servicio.
- Forzar AES y revisar SPNs innecesarios.
- Auditar 4104 con firmas de Rubeus/`GetNPUsers`.

MITRE: T1558.004, T1558.003, T1078.
