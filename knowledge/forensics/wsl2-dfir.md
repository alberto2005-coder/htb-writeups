---
title: WSL2 en DFIR — artefactos del host y captura de API
tags: [forensics, dfir, wsl2, windows, api-monitor, vhdx]
---

# WSL2 en DFIR: el punto ciego y cómo abrirlo

[🇬🇧 English](wsl2-dfir.en.md) | **Español**

## 1. Por qué WSL2 es un punto ciego

WSL2 ejecuta un kernel Linux real dentro de una VM ligera. Lo que ocurre dentro —procesos ELF, historial de shell, conexiones, ficheros preparados— **no genera Prefetch, ni 4688, ni Sysmon de proceso** en el host. Sysmon solo ve los accesos a utilidades de Windows (`/mnt/c/...`, `powershell.exe`).

Consecuencia práctica: si el investigador solo mira artefactos Windows, el atacante que trabaja dentro de la distro es invisible.

## 2. Artefactos en el host

**Registro.** Cada distro registrada vive en `HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss\<GUID>`:

| Valor | Contenido |
|---|---|
| `BasePath` | ruta del sistema de ficheros (por defecto `%LOCALAPPDATA%\Packages\...\LocalState`) |
| `DistributionName` | nombre de la distro |
| `Version` | 1 o 2 |
| `DefaultUid` | UID por defecto |

**Disco.** En WSL2, dentro de `BasePath` está `ext4.vhdx`: el sistema de ficheros completo. Es la evidencia principal.

**Ejecución en Windows.** Prefetch de `wsl.exe` y `wslhost.exe`, y eventos de Hyper-V (`Microsoft-Windows-Hyper-V-VmSwitch-Operational`) que muestran cuándo arrancó la VM.

## 3. Montar el disco

Con la distro apagada (`wsl --shutdown`), se adjunta en modo *bare* para no montarlo automáticamente:

```powershell
wsl.exe --mount "C:\Users\<USER>\AppData\Local\Packages\<DISTRO>\LocalState\ext4.vhdx" --vhd --bare
```

Desde otra distro, se identifica el dispositivo y se monta en solo lectura:

```bash
lsblk
mkdir -p /mnt/evidence
mount -o ro /dev/sdX /mnt/evidence
```

Alternativa multiplataforma con libguestfs:

```bash
guestmount --add ext4.vhdx --ro -i ./import/
```

Con el sistema de ficheros montado, el análisis es Linux normal: `~/.bash_history`, `~/.zsh_history`, `/var/log`, `/tmp`, `crontab`, claves SSH, `.gitconfig`, binarios ELF descargados.

## 4. Captura de API: ver lo que Windows no registra

La técnica publicada por HTB (julio 2023) es enganchar las APIs Win32 que WSL2 usa para hablar con el kernel: `RtlUnicodeToUTF8N` (conversión de cadenas entre el lado Linux y el NT) y `WriteFile` (escritura en los handles de pipe/socket que transportan la consola y los datos).

- **API Monitor** guarda capturas en `.apmx64`. Ese fichero **es un ZIP**: al descomprimirlo hay un blob por proceso monitorizado.
- Los blobs son memoria capturada, no texto: `strings` en ASCII y en UTF-16LE recupera comandos tecleados, contenido de ficheros y respuestas de red.
- En una captura, `RtlUnicodeToUTF8N` con una cadena larga y `WriteFile` sobre un handle hacia fuera es el patrón de una exfiltración desde la distro.

```bash
unzip -o Employee.apmx64 -d employee/
strings -a  employee/* | grep -i "powershell\|cat \|curl\|Invoke-"
strings -el employee/* | head
```

## 5. Del guest al host

Puentes que hay que conocer:

- **`/mnt/c`**: acceso directo al disco de Windows; un ELF puede escribir en `C:\Users\...` sin dejar proceso hijo en Windows.
- **Interop**: `powershell.exe`, `cmd.exe` o `wsl.exe` invocados desde Linux sí crean proceso en Windows; ahí vuelve a haber telemetría.
- **`lsassy`** desde la distro: usa `sekurlsa`/`comsvcs` contra el host vía `powershell.exe` o RPC, con lo que el binario malicioso nunca toca disco de Windows.

## 6. Correlación

```text
Lxss (BasePath + Version 2)
  → Prefetch de wsl.exe
  → captura de API con RtlUnicodeToUTF8N + WriteFile
  → 4688/4104 solo si hubo interop con PowerShell
```

La pregunta típica del Sherlock —«¿qué API usa WSL2 para escribir en el pipe?»— se responde con la arquitectura, no con un evento: `WriteFile`.

## 7. Detección y mitigación

- Deshabilitar WSL donde no se use (`dism /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux`) y restringir su instalación por política.
- EDR con visibilidad WSL (la cobertura es desigual; no asumir que el guest está monitorizado).
- Alertar de `wsl.exe` desde procesos no interactivos, de escrituras en `LocalState\ext4.vhdx` fuera de uso normal y de interop hacia `powershell.exe`.
- En respuesta: apagar la distro, preservar `ext4.vhdx` y el registro `Lxss`, y analizar el VHDX en solo lectura.

MITRE: T1059.004 (Unix shell), T1041, T1567, T1070.
