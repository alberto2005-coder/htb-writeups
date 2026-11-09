---
title: CrownJewel-2
category: DFIR / Active Directory
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, pass-the-hash, smb, evtx]
sherlock: CrownJewel-2
domain: DFIR
---


# CrownJewel-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

## Escenario

Continuación del compromiso de CrownJewel-1: el atacante ya tiene una cuenta y se mueve por el dominio. La evidencia son logs de eventos de los DC y del host comprometido; hay que reconstruir el movimiento lateral y distinguirlo del tráfico administrativo legítimo.

## Evidencias

```bash
unzip crownjewel2.zip        # contraseña habitual: hacktheblue
sha256sum *                  # inventario antes de tocar nada
EvtxECmd.exe -d Logs --csv out --csvf all.csv
```

Canales útiles: `Security.evtx`, `System.evtx`, `Microsoft-Windows-Sysmon/Operational`, `PowerShell/Operational` y el log del servicio SMB.

## Investigación

1. ¿Con qué cuenta se autenticó el atacante por primera vez tras el compromiso?
2. ¿Qué hosts recibieron ese logon y en qué orden?
3. ¿Se usó hash en lugar de contraseña?
4. ¿Qué recurso se leyó o copió?

- Filtrar **4624 tipo 3** y **tipo 10**, agrupando por `TargetUserName`, `IpAddress` y hora. Un mismo usuario apareciendo en hosts donde nunca trabaja es la señal.
- **4624 con `AuthenticationPackage` NTLM** y `LogonProcess` vacío/`NtLmSsp` apunta a *pass-the-hash*; Kerberos tendría `Kerberos` y un TGT previo.
- Cruzar con **5140/5145** para ver qué share se abrió y **4662** si se tocó AD.
- Los **4768/4769** del DC dan el contexto: si no hay TGT para esa cuenta antes del 4624, el logon fue por hash o por credencial en claro.

## Conclusiones

```text
4624 type 3  user=<cuenta>  src=<host atacante>  auth=NTLM
5145         share=\\<host>\C$  access=ReadData
4662         object=DC=<dominio>  DS-Replication-Get-Changes
```

La combinación NTLM + acceso a `C$` + lectura de AD sin TGT previo describe el movimiento y el objetivo; no es un logon interactivo normal.

## Lecciones

- El *pass-the-hash* no genera 4768: la ausencia de Kerberos es tan informativa como la presencia de un 4624.
- Comparar con la línea base del usuario evita falsos positivos de herramientas de administración.
- Los shares administrativos (`C$`, `ADMIN$`) son el mejor indicador de lateral movement.

- Alertar de 4624 tipo 3 con NTLM desde hosts que no son de administración.
- Proteger cuentas privilegiadas (LAPS, `Protected Users`, credenciales restringidas).
- Segmentar y limitar `C$`/`ADMIN$`; auditar 5140/5145.
- Rotar el hash comprometido y revisar sesiones activas.

MITRE: T1550.002, T1021.002, T1078.
