---
sherlock: "OpSalwarKameez24-2: Magic-Show"
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, kape, evtx, memory, rdp]
---

# OpSalwarKameez24-2: Magic-Show — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Los administradores de StoreD Technologies detectan equipos Windows 11 que se reinician para aplicar actualizaciones en horario laboral. La política solo permite hacerlo de noche. Se entrega un triaje KAPE y un volcado de memoria de uno de los equipos.

## Evidencias

- Salida de KAPE con `C\`, `Windows\System32\winevt` y `$MFT`.
- Volcado de memoria del equipo afectado.
- Registros de actualizaciones y de sesiones RDP.

```bash
tree -L 2 KAPE
sha256sum memory.raw
```

## Investigación

### 1. Inventario y triaje

Se revisan los EVTX de Security, System, PowerShell y TerminalServices. Se busca el primer inicio de sesión anómalo y se compara con la ventana de reinicios. `EvtxECmd` o `Chainsaw` aceleran la correlación.

```bash
EvtxECmd.exe -d KAPE/C/Windows/System32/winevt/Logs --csv out
```

### 2. Línea temporal

Un usuario comprometido inicia sesión por RDP y lanza `wuauclt` o `UsoClient` fuera de horario. Los eventos de servicio muestran la instalación y el reinicio. El volcado de memoria conserva el proceso que coordinó la acción y sus conexiones.

```bash
vol -f memory.raw windows.pslist
vol -f memory.raw windows.netscan
```

### 3. Artefacto clave

El evento de creación de servicio y la clave de ejecución apuntan a un mecanismo de persistencia. La cuenta comprometida aparece en el logon tipo 10 y en los procesos hijos. La combinación explica por qué las actualizaciones se aplicaron durante el día.

## Conclusiones

- Los reinicios no fueron un fallo de Windows Update.
- Un atacante usó una cuenta comprometida y RDP.
- La persistencia se apoyó en un servicio o tarea programada.
- Hay que rotar credenciales y revisar el resto de equipos.

## Lecciones

- KAPE reduce el ruido, pero hay que validar la hora y la zona horaria.
- Los eventos 4624 tipo 10 y 7045 son clave.
- La memoria y los EVTX se complementan.
- Una política de actualizaciones no impide que un atacante la invoque.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://writeups.chicken0248.fyi/HackTheBox/HTB%20Labs/HTB%20Sherlocks/%5bHTB%20Sherlocks%20Write-up%5d%20OpSalwarKameez24-2%20Magic-Show>
- <https://attack.mitre.org/techniques/T1078/002/>
