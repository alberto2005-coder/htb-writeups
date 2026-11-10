---
sherlock: i-like-to
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, moveit, cve-2023-34362, iis, mft, evtx, memory, webshell]
---

# i-like-to — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Un servidor **MOVEit Transfer** expuesto a internet ha sido comprometido. La organización entrega un triaje de KAPE del sistema de ficheros, los logs de IIS del día del incidente, el volcado de la base de datos de la aplicación y una imagen de memoria de 4 GB. Hay que reconstruir cómo entró el atacante, qué dejó y qué se llevó.

## Evidencias

```text
I-like-to-27a787c5.vmem                       imagen de memoria (sin .vmss)
Triage/uploads/auto/C%3A/inetpub/logs/LogFiles/W3SVC2/u_ex230712.log
Triage/uploads/auto/C%3A/Windows/System32/winevt/Logs/   EVTX del sistema
Triage/uploads/auto/C%3A/users/                          historial de PSReadLine
Triage/uploads/ntfs/%5C%5C.%5CC%3A/$MFT                  MFT en crudo
Triage/uploads/moveit.sql                                volcado de la BD
```

```bash
sha256sum Triage.zip I-like-to-27a787c5.vmem   # anotar antes de tocar nada
```

La imagen no trae el `.vmss`, así que Volatility no puede reconstruir las capas de memoria: para esa pieza hay que quedarse en `strings`.

## Investigación

### 1. Inventario y triaje

Se empieza por lo que da contexto rápido: los logs de IIS y el `$MFT`. El log de IIS se lee sin herramientas y da la secuencia de peticiones con hora UTC; el MFT se convierte a CSV para tener creación, modificación y cambio de registro de cada fichero:

```bash
C:/Tools/ZimmermanTools/MFTECmd.exe -f '$MFT' --csv mft_out/
C:/Tools/ZimmermanTools/EvtxECmd.exe -d Logs --json evtx_out/
strings I-like-to-27a787c5.vmem > mem.strings
strings -e l I-like-to-27a787c5.vmem >> mem.strings
```

Del triaje se abre primero `u_ex230712.log` porque es el único sitio donde quedan las peticiones HTTP completas: método, ruta, código, user-agent y IP de origen.

### 2. Línea temporal

Los logs de IIS usan **UTC** en el campo de fecha y hora, igual que los EVTX y el MFT, así que la correlación no necesita conversiones: es una de las razones por las que este caso se resuelve rápido.

Orden de los hechos:

1. Barrido con `nmap` contra el servidor (el user-agent del escáner queda en el log).
2. Peticiones POST a `machine2.aspx` con user-agent `Ruby`: es el exploit de Metasploit de CVE-2023-34362, que usa ese componente para la inyección SQL y la deserialización.
3. Cambio de contraseña de la cuenta de servicio (`4724`), seguido de un inicio de sesión **tipo 10** (RDP) con esa misma cuenta.
4. Primer intento de webshell: `moveit.asp` en `C:\inetpub\wwwroot`. Falla porque el servidor no tiene ASP clásico habilitado y además Defender lo pone en cuarentena.
5. Segundo intento: `move.aspx` en `C:\MOVEitTransfer\wwwroot`, que sí se ejecuta.
6. Uso de la webshell y extracción de datos.

### 3. Artefacto clave

El **registro del MFT** de `move.aspx` cierra el caso: está en `C:\MOVEitTransfer\wwwroot`, con un tamaño de 1400 bytes y una hora de creación que coincide con la petición del log. Además aparece su copia compilada por .NET en `Windows\Microsoft.NET\Framework64\v4.0.30319\Temporary ASP.NET Files\root\...`, con la hora en que el atacante la ejecutó por primera vez.

```bash
grep 'move.aspx' mft_out/*.csv | cut -d, -f6-9,20-27
```

En `mem.strings` quedan tres pruebas que completan el cuadro:

- El comando de descarga de la webshell, un `wget` de PowerShell apuntando a la IP del atacante y al puerto 9001.
- El título de la shell, **awen asp.net webshell**, que identifica la familia.
- El comando `net user` con el que se cambió la contraseña de la cuenta de servicio.

El volcado SQL aporta el `InstID` de la instancia, el identificador con el que se generó el token de la webshell; sirve para demostrar que la shell se creó desde la propia aplicación y no se subió por otro canal.

## Conclusiones

- Entrada: explotación de **CVE-2023-34362** (inyección SQL en MOVEit Transfer) con el módulo de Metasploit, repetida durante casi una hora.
- Persistencia: webshell ASPX (`move.aspx`) en el directorio de la aplicación, precedida de un intento fallido en ASP.
- Acceso interactivo: cambio de contraseña de la cuenta de servicio y RDP con ella.
- Indicadores: user-agent `Ruby` en POST a `machine2.aspx`, peticiones a `move.aspx`, `wget` desde PowerShell, título `awen asp.net webshell` y la ruta de compilación .NET de la shell.
- Lección de método: el intento fallido de `moveit.asp` y su cuarentena por Defender son parte de la historia; ignorarlos dejaría un hueco en la línea temporal.

## Lecciones

- Un EDR que bloquea el primer intento no evita el segundo: la detección tiene que cubrir la escritura de `.aspx` por el proceso de IIS.
- El log de IIS y el MFT se complementan: el log dice "cuándo se pidió", el MFT dice "cuándo existió el fichero en disco".
- El historial de PSReadLine y los `strings` de memoria recuperan comandos que ningún log de aplicación guarda.
- Mitigación: parchear MOVEit, restringir la escritura en `wwwroot`, alertar de `w3wp.exe` creando ejecutables y revisar los cambios de contraseña de cuentas de servicio (`4724`).
- Lo que faltaría en la organización: captura de memoria completa (con `.vmss`) y retención de logs de IIS más allá de unos días.

MITRE: T1190 (exploit public-facing application), T1505.003 (web shell), T1059.001 (PowerShell), T1021.001 (RDP), T1098 (account manipulation).
